from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Message, UserActivity
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import json

@login_required
def chat_room(request):
    return render(request, 'chat/chat.html')

@login_required
def message_list(request):
    # Update user activity
    UserActivity.objects.update_or_create(
        user=request.user,
        defaults={'last_seen': timezone.now()}
    )

    if request.method == 'GET':
        # Get messages (Public OR Private involving the user)
        messages = Message.objects.filter(
            Q(recipient__isnull=True) | 
            Q(recipient=request.user) | 
            Q(user=request.user)
        ).order_by('timestamp')
        
        messages_data = [{
            'user': msg.user.username, 
            'content': msg.content, 
            'timestamp': msg.timestamp.strftime('%H:%M'),
            'recipient': msg.recipient.username if msg.recipient else None,
            'is_private': msg.recipient is not None
        } for msg in messages]

        # Get online users (active in last 5 minutes)
        time_threshold = timezone.now() - timedelta(minutes=5)
        online_users = UserActivity.objects.filter(last_seen__gte=time_threshold).select_related('user')
        users_data = [{'username': activity.user.username} for activity in online_users]

        return JsonResponse({'messages': messages_data, 'online_users': users_data})
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('content')
            recipient_username = data.get('recipient')
            
            if content:
                recipient = None
                if recipient_username:
                    User = get_user_model()
                    try:
                        recipient = User.objects.get(username=recipient_username)
                    except User.DoesNotExist:
                        pass # Or handle error
                
                Message.objects.create(user=request.user, content=content, recipient=recipient)
                return JsonResponse({'status': 'ok'})
            return JsonResponse({'status': 'error', 'message': 'Empty content'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)
