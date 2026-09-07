import json
from datetime import timedelta
from uuid import UUID

from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from .models import StreamParticipant, StreamRoom, StreamSignal


def error(message, status=400):
    return JsonResponse({'error': message}, status=status)


def valid_signal(payload):
    if not isinstance(payload, dict):
        return False
    if payload.get('type') in ('reset', 'retry'):
        return set(payload) == {'type'}
    if payload.get('type') in ('offer', 'answer'):
        return isinstance(payload.get('sdp'), str) and len(payload['sdp']) <= 65536
    candidate = payload.get('candidate')
    return (isinstance(candidate, dict) and
            isinstance(candidate.get('candidate'), str) and
            len(candidate['candidate']) <= 4096)


@never_cache
@require_POST
def exchange(request, stream_id):
    if not request.user.is_authenticated:
        return error('Sua sessao expirou. Entre novamente.', 401)
    if request.user.is_expired and not request.user.is_superuser:
        return error('Acesso expirado.', 403)
    if len(request.body) > 262144:
        return error('Mensagens muito grandes.', 413)
    try:
        body = json.loads(request.body)
        participant_id = UUID(body['client_id'])
        role = body['role']
        cursor = body.get('cursor', 0)
        outgoing = body.get('messages', [])
        if role not in ('host', 'viewer') or type(cursor) is not int or cursor < 0:
            raise ValueError
        if not isinstance(outgoing, list) or len(outgoing) > 64:
            raise ValueError
        messages = []
        for message in outgoing:
            if not valid_signal(message['signal']):
                raise ValueError
            messages.append((UUID(message['id']), UUID(message['to']),
                             UUID(message['connection_id']), message['signal']))
    except (ValueError, TypeError, KeyError, AttributeError):
        return error('Mensagem de conexao invalida.')

    now = timezone.now()
    active_since = now - timedelta(seconds=180)
    # Serialize exchanges in a room so retries, acknowledgments and host replacement agree.
    with transaction.atomic():
        stream = StreamRoom.objects.select_for_update().filter(pk=stream_id).first()
        if not stream or not stream.is_live:
            return error('Transmissao encerrada.', 404)
        if role == 'host' and stream.host_id != request.user.pk:
            return error('Somente o transmissor pode publicar nesta sala.', 403)
        participant, created = StreamParticipant.objects.get_or_create(
            pk=participant_id,
            defaults={'stream': stream, 'user': request.user, 'role': role},
        )
        if (participant.stream_id != stream.pk or participant.user_id != request.user.pk or
                participant.role != role):
            return error('Sessao de conexao invalida.', 403)
        if participant.closed:
            return error('Esta conexao foi encerrada ou substituida.', 410)
        if body.get('leave') is True:
            participant.closed = True
            participant.save(update_fields=['closed'])
            return JsonResponse({'closed': True})
        if created and role == 'host':
            stream.participants.filter(role='host').exclude(pk=participant.pk).update(closed=True)
        participant.last_seen = now
        participant.ready = body.get('ready') is True
        participant.save(update_fields=['last_seen', 'ready'])

        others = stream.participants.filter(closed=False, last_seen__gte=active_since).exclude(role=role)
        targets = {str(item.pk): item for item in others.select_related('user')}
        accepted = []
        for message_id, target_id, connection_id, payload in messages:
            target = targets.get(str(target_id))
            if target:
                if StreamSignal.objects.filter(target=target, delivered=False).count() >= 1000:
                    return error('Fila de conexao cheia. Tente novamente.', 429)
                StreamSignal.objects.get_or_create(
                    message_id=message_id,
                    defaults={'source': participant, 'target': target,
                              'connection_id': connection_id, 'payload': payload},
                )
            # An expired target cannot receive this message; let clients discard it.
            accepted.append(str(message_id))

        # Retain acknowledged message IDs briefly: the sender may retry a lost HTTP response.
        StreamSignal.objects.filter(target=participant, id__lte=cursor, delivered=False).update(delivered=True)
        incoming = list(StreamSignal.objects.filter(target=participant, id__gt=cursor, delivered=False)
                        .order_by('id')[:128])
        if role == 'host':
            StreamSignal.objects.filter(source__stream=stream, created_at__lt=now - timedelta(minutes=5)).delete()
        if created:
            stream.participants.filter(last_seen__lt=now - timedelta(days=1)).exclude(pk=participant.pk).delete()
        return JsonResponse({
            'accepted': accepted,
            'participants': [{'id': key, 'username': target.user.username, 'ready': target.ready}
                             for key, target in targets.items()],
            'messages': [{'seq': item.pk, 'from': str(item.source_id),
                          'connection_id': str(item.connection_id), 'signal': item.payload}
                         for item in incoming],
            'cursor': incoming[-1].pk if incoming else cursor,
        })
