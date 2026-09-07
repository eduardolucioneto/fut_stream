from django.urls import path
from . import views
from . import signaling

urlpatterns = [
    path('signal/<int:stream_id>/', signaling.exchange, name='stream_signal'),
    path('start/', views.start_stream, name='start_stream'),
    path('start-broadcast/<int:game_id>/', views.start_broadcast, name='start_broadcast'),
    path('broadcast/<int:stream_id>/', views.broadcast_room, name='broadcast_room'),
    path('watch/<int:game_id>/', views.watch_stream, name='watch_stream'),
    path('stop/<int:stream_id>/', views.stop_stream, name='stop_stream'),
    path('end/<int:stream_id>/', views.end_stream, name='end_stream'),
    path('delete/<int:stream_id>/', views.delete_stream, name='delete_stream'),
    path('delete-game/<int:game_id>/', views.delete_game, name='delete_game'),
    path('calculator/', views.calculator, name='calculator'),
]
