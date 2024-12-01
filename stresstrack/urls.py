from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/task', views.dash_task, name='dash_task'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
]