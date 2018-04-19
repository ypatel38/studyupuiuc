from django.urls import path
from django.contrib.auth.views import login, logout #built-in django authentication system
from map.views import *

urlpatterns = [
    path('', MapView.as_view(), name='map'),
]

app_name = 'map'
