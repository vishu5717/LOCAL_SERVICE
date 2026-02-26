from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('signup/',views.userSignupView,name='signup'),
    path('', views.homeView, name='home'),
    path('services/', views.serviceListView, name='service_list'),
    path('login/',views.userLoginView,name='login')

]