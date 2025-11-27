from django.urls import path
from . import views

urlpatterns = [
    path('upgrade/', views.upgrade, name='upgrade'),
]
