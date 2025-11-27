from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from schedule.models import GameEvent
from django.utils import timezone

def home(request):
    live_games = GameEvent.objects.filter(status='LIVE').order_by('date_time')
    upcoming_games = GameEvent.objects.filter(status='UPCOMING').order_by('date_time')
    past_games = GameEvent.objects.filter(status='ENDED').order_by('-date_time')
    
    context = {
        'live_games': live_games,
        'upcoming_games': upcoming_games,
        'past_games': past_games,
    }
    return render(request, 'core/home.html', context)

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        
        # Compose email
        full_message = f"""
Nova mensagem de contato do TopTraders:

Nome: {name}
Email: {email}
Assunto: {subject}

Mensagem:
{message}
        """
        
        try:
            # Send email to both addresses
            send_mail(
                subject=f'[TopTraders] {subject}',
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['eduardolucioneto@gmail.com', 'studioduzao@gmail.com'],
                fail_silently=False,
            )
            return render(request, 'core/contact.html', {'success': True})
        except Exception as e:
            return render(request, 'core/contact.html', {'error': True})
            
    return render(request, 'core/contact.html')

def promote_to_admin(request, username):
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
        
        # Check if already admin
        if user.is_superuser:
            return HttpResponse(f"""
                <h1>ℹ️ User '{username}' is already a superuser!</h1>
                <p>Access <a href="/admin/">/admin/</a> to login.</p>
                <p><strong>⚠️ IMPORTANT:</strong> Delete this view for security!</p>
            """)
        
        # Promote to admin
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        return HttpResponse(f"""
            <h1>✅ User '{username}' promoted to superuser!</h1>
            <p><strong>Username:</strong> {username}</p>
            <p><strong>Password:</strong> (your existing password)</p>
            <p><strong>⚠️ IMPORTANT:</strong></p>
            <ul>
                <li>Access <a href="/admin/">/admin/</a> and login</li>
                <li>Change your password if needed</li>
                <li><strong>DELETE this view from core/views.py</strong></li>
                <li><strong>Remove the URL from core/urls.py</strong></li>
            </ul>
        """)
        
    except User.DoesNotExist:
        return HttpResponse(f"""
            <h1>❌ User '{username}' not found!</h1>
            <p>Make sure you:</p>
            <ol>
                <li>Contact the site administrator to request an account (registrations are handled by administrators)</li>
                <li>Typed the username correctly (case-sensitive)</li>
            </ol>
        """)
    except Exception as e:
        return HttpResponse(f"Error: {e}")
