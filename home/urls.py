from django.urls import path
from home.views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('new-session/', NewSessionView.as_view(), name='new_session'),
]

app_name = 'home'
