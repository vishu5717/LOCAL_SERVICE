 
from django.urls import path
from . import views

urlpatterns = [
    
    path('owner-dashboard/', views.ownerDashboardView, name='owner_dashboard'),
    path('user-dashboard/', views.userDashboardView, name='user_dashboard'),
]