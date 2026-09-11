import json
from datetime import timedelta
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from schedule.models import GameEvent
from .models import StreamParticipant, StreamRoom, StreamSignal


@override_settings(SECURE_SSL_REDIRECT=False, LIVEKIT_URL='wss://livekit.test', LIVEKIT_API_KEY='testkey', LIVEKIT_API_SECRET='testsecret-with-at-least-32-characters')
class SignalingTests(TestCase):
    def setUp(self):
        self.host = get_user_model().objects.create_user('host')
        self.viewer = get_user_model().objects.create_user('viewer')
        self.other = get_user_model().objects.create_user('other')
        self.game = GameEvent.objects.create(title='Test', date_time=timezone.now(),
            team_a='A', team_b='B', created_by=self.host)
        self.room = StreamRoom.objects.create(host=self.host, game=self.game, title='Test', is_live=True)
        self.url = reverse('stream_signal', args=[self.room.pk])
        self.host_id, self.viewer_id = str(uuid4()), str(uuid4())

    def exchange(self, user, client_id, role, **extra):
        self.client.force_login(user)
        return self.client.post(self.url, json.dumps({'client_id': client_id, 'role': role,
            'ready': True, **extra}), content_type='application/json')

    def join(self):
        self.exchange(self.host, self.host_id, 'host')
        self.exchange(self.viewer, self.viewer_id, 'viewer')

    def offer(self, **extra):
        return {'id': str(uuid4()), 'to': self.viewer_id, 'connection_id': str(uuid4()),
                'signal': {'type': 'offer', 'sdp': 'v=0\r\n'}, **extra}

    def test_requires_login(self):
        self.assertEqual(self.client.post(self.url, '{}', content_type='application/json').status_code, 401)

    def test_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.viewer)
        self.assertEqual(client.post(self.url, '{}', content_type='application/json').status_code, 403)

    def test_only_room_host_can_register_as_host(self):
        response = self.exchange(self.viewer, self.viewer_id, 'host')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(StreamParticipant.objects.count(), 0)

    def test_expired_viewer_is_denied(self):
        self.viewer.valid_until = timezone.now().date() - timedelta(days=1)
        self.viewer.save()
        self.assertEqual(self.exchange(self.viewer, self.viewer_id, 'viewer').status_code, 403)

    def test_sessions_are_bound_to_user_and_role(self):
        self.join()
        self.assertEqual(self.exchange(self.other, self.viewer_id, 'viewer').status_code, 403)
        self.assertEqual(self.exchange(self.host, self.host_id, 'viewer').status_code, 403)

    def test_offer_answer_delivery_and_acknowledgment(self):
        self.join()
        message = self.offer()
        self.assertEqual(self.exchange(self.host, self.host_id, 'host', messages=[message]).status_code, 200)
        body = self.exchange(self.viewer, self.viewer_id, 'viewer').json()
        self.assertEqual(body['messages'][0]['signal'], message['signal'])
        self.assertEqual(body['messages'][0]['from'], self.host_id)
        answer = self.offer(to=self.host_id, signal={'type': 'answer', 'sdp': 'v=0\r\n'})
        answer['connection_id'] = message['connection_id']
        self.exchange(self.viewer, self.viewer_id, 'viewer', cursor=body['cursor'], messages=[answer])
        self.assertFalse(StreamSignal.objects.filter(target_id=self.viewer_id, delivered=False).exists())
        received = self.exchange(self.host, self.host_id, 'host').json()['messages']
        self.assertEqual(received[0]['signal']['type'], 'answer')

    def test_retrying_a_lost_response_does_not_duplicate_signals(self):
        self.join()
        message = self.offer()
        for _ in range(2):
            self.exchange(self.host, self.host_id, 'host', messages=[message])
        self.assertEqual(StreamSignal.objects.count(), 1)
        first = self.exchange(self.viewer, self.viewer_id, 'viewer').json()
        second = self.exchange(self.viewer, self.viewer_id, 'viewer').json()
        self.assertEqual(first['messages'], second['messages'])

    def test_retry_after_recipient_ack_does_not_redeliver_offer(self):
        self.join()
        message = self.offer()
        self.exchange(self.host, self.host_id, 'host', messages=[message])
        received = self.exchange(self.viewer, self.viewer_id, 'viewer').json()
        self.exchange(self.viewer, self.viewer_id, 'viewer', cursor=received['cursor'])
        self.exchange(self.host, self.host_id, 'host', messages=[message])
        self.assertEqual(self.exchange(self.viewer, self.viewer_id, 'viewer', cursor=received['cursor']).json()['messages'], [])

    def test_viewers_cannot_exchange_messages_with_each_other(self):
        self.join()
        other_id = str(uuid4())
        self.exchange(self.other, other_id, 'viewer')
        self.exchange(self.viewer, self.viewer_id, 'viewer', messages=[self.offer(to=other_id)])
        self.assertEqual(StreamSignal.objects.count(), 0)

    def test_cross_room_messages_are_not_delivered(self):
        self.join()
        another_room = StreamRoom.objects.create(host=self.other, title='Other', is_live=True)
        target = StreamParticipant.objects.create(stream=another_room, user=self.other, role='viewer')
        self.exchange(self.host, self.host_id, 'host', messages=[self.offer(to=str(target.pk))])
        self.assertEqual(StreamSignal.objects.count(), 0)

    def test_new_host_tab_replaces_the_old_session_without_reopening_it(self):
        self.join()
        new_id = str(uuid4())
        self.exchange(self.host, new_id, 'host')
        self.assertEqual(self.exchange(self.host, self.host_id, 'host').status_code, 410)
        active = self.exchange(self.viewer, self.viewer_id, 'viewer').json()['participants']
        self.assertEqual([item['id'] for item in active], [new_id])

    def test_ended_stream_rejects_signaling(self):
        self.room.is_live = False
        self.room.save()
        self.assertEqual(self.exchange(self.viewer, self.viewer_id, 'viewer').status_code, 404)

    def test_leave_cannot_be_undone_by_an_in_flight_poll(self):
        self.join()
        self.exchange(self.viewer, self.viewer_id, 'viewer', leave=True)
        self.assertEqual(self.exchange(self.viewer, self.viewer_id, 'viewer').status_code, 410)

    def test_stale_participants_are_not_advertised(self):
        self.join()
        StreamParticipant.objects.filter(pk=self.viewer_id).update(last_seen=timezone.now() - timedelta(minutes=4))
        self.assertEqual(self.exchange(self.host, self.host_id, 'host').json()['participants'], [])

    def test_invalid_and_oversized_signals_are_rejected(self):
        self.join()
        for signal in [None, {}, {'type': 'offer', 'sdp': 'x' * 65537}, {'candidate': 1}]:
            with self.subTest(signal_type=type(signal)):
                self.assertEqual(self.exchange(self.host, self.host_id, 'host', messages=[self.offer(signal=signal)]).status_code, 400)
        self.assertEqual(StreamSignal.objects.count(), 0)

    def test_signaling_cannot_be_cached(self):
        response = self.exchange(self.viewer, self.viewer_id, 'viewer')
        self.assertIn('no-store', response['Cache-Control'])

    def test_watch_uses_latest_live_room_and_local_scripts(self):
        latest = StreamRoom.objects.create(host=self.host, game=self.game, title='Latest', is_live=True)
        self.client.force_login(self.viewer)
        response = self.client.get(reverse('watch_stream', args=[self.game.pk]))
        self.assertEqual(response.context['stream'].pk, latest.pk)
        self.assertContains(response, 'livekit-connection')
        self.assertContains(response, 'livekit-client.umd.min.js')
        self.assertNotContains(response, 'simplepeer-9.11.1.min.js')
        self.assertNotContains(response, 'stream-connection')
