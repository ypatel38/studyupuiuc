from django.urls import path
from django.conf.urls import include, url
from django.contrib.auth.views import login, logout #built-in django authentication system
from accounts.views import *
from .views import RegisterView
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', login, {'template_name': 'accounts/login.html'}, name='login'),
    path('logout/', logout, {'template_name': 'accounts/logout.html'}, name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        RegisterView.activate, name='activate'),
]

app_name = 'accounts'
