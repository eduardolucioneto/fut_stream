from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_room, name='chat_room'),
    path('api/messages/', views.message_list, name='message_list'),
]
