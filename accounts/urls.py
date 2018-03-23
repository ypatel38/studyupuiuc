from django.urls import path
from django.contrib.auth.views import login, logout #built-in django authentication system
from accounts.views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', login, {'template_name': 'accounts/login.html'}, name='login'),
    path('logout/', logout, {'template_name': 'accounts/logout.html'}, name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
]

app_name = 'accounts'
