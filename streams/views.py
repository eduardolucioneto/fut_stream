from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import StreamRoom
from schedule.models import GameEvent

from django.utils import timezone

@login_required
def start_stream(request):
    # allow admin users (staff/superuser) to create/start streams too
    if not (request.user.can_create_stream or request.user.is_staff or request.user.is_superuser):
        return redirect('home')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip() or 'default'
        team_a = request.POST.get('team_a', '').strip() or 'default'
        team_b = request.POST.get('team_b', '').strip() or 'default'
        date_time_str = request.POST.get('date_time', '').strip()
        
        # Parse datetime or use current time
        if date_time_str:
            from datetime import datetime
            date_time = datetime.fromisoformat(date_time_str)
            # Make it timezone-aware
            date_time = timezone.make_aware(date_time)
        else:
            date_time = timezone.now()
        
        # Create GameEvent with UPCOMING status (not LIVE)
        game = GameEvent.objects.create(
            title=title,
            date_time=date_time,
            team_a=team_a,
            team_b=team_b,
            status='UPCOMING',
            created_by=request.user
        )
        
        return redirect('home')
    return render(request, 'streams/start_stream.html')

@login_required
def start_broadcast(request, game_id):
    # allow admins to start broadcasts for any game
    if not (request.user.can_create_stream or request.user.is_staff or request.user.is_superuser):
        return redirect('home')

    if request.user.is_staff or request.user.is_superuser:
        game = get_object_or_404(GameEvent, id=game_id)
    else:
        game = get_object_or_404(GameEvent, id=game_id, created_by=request.user)
    if request.method == 'POST':
        # Create StreamRoom and set game to LIVE
        stream = StreamRoom.objects.create(
            host=request.user,
            title=game.title,
            is_live=True,
            game=game
        )
        game.status = 'LIVE'
        game.save()
        game.save()
        from django.urls import reverse
        url = reverse('broadcast_room', args=[stream.id])
        return redirect(f'{url}?auto_start=true')
    return redirect('home')


@login_required
def broadcast_room(request, stream_id):
    stream = get_object_or_404(StreamRoom, id=stream_id, host=request.user)
    return render(request, 'streams/broadcast.html', {'stream': stream})

@login_required
def watch_stream(request, game_id):
    # Check if user is expired
    if request.user.is_expired and not request.user.is_superuser:
        return render(request, 'streams/expired.html')

    # Find the stream associated with the game
    stream = get_object_or_404(StreamRoom, game__id=game_id)
    return render(request, 'streams/watch.html', {'stream': stream})

@login_required
def stop_stream(request, stream_id):
    # Allow deletion if user is host OR has delete permission
    # allow admins to stop streams regardless of host
    if request.user.can_delete_stream or request.user.is_staff or request.user.is_superuser:
        stream = get_object_or_404(StreamRoom, id=stream_id)
    else:
        stream = get_object_or_404(StreamRoom, id=stream_id, host=request.user)
        
    if request.method == 'POST':
        # Delete the StreamRoom to allow restarting
        stream.delete()
    return redirect('home')

@login_required
def end_stream(request, stream_id):
    # Allow ending if user is host OR has delete permission (moderator action)
    # allow admins to end streams regardless of host
    if request.user.can_delete_stream or request.user.is_staff or request.user.is_superuser:
        stream = get_object_or_404(StreamRoom, id=stream_id)
    else:
        stream = get_object_or_404(StreamRoom, id=stream_id, host=request.user)
        
    if request.method == 'POST':
        stream.is_live = False
        stream.save()
        if stream.game:
            stream.game.status = 'ENDED'
            stream.game.save()
    return redirect('home')

@login_required
def delete_stream(request, stream_id):
    # allow admins to delete streams regardless of host
    if request.user.can_delete_stream or request.user.is_staff or request.user.is_superuser:
        stream = get_object_or_404(StreamRoom, id=stream_id)
    else:
        stream = get_object_or_404(StreamRoom, id=stream_id, host=request.user)
        
    if request.method == 'POST':
        game = stream.game
        if game:
            game.delete()  # Cascade will delete stream
    return redirect('home')

@login_required
def delete_game(request, game_id):
    # allow admins to delete games regardless of creator
    if request.user.can_delete_stream or request.user.is_staff or request.user.is_superuser:
        game = get_object_or_404(GameEvent, id=game_id)
    else:
        game = get_object_or_404(GameEvent, id=game_id, created_by=request.user)
        
    if request.method == 'POST':
        game.delete()  # Cascade will delete associated streams
    return redirect('home')

@login_required
def calculator(request):
    return render(request, 'streams/calculator.html')
