from django.urls import path, re_path
from home.views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('new-session/', NewSessionView.as_view(), name='new_session'),
    path('edit-session/<seshID>/', EditSessionView.as_view(), name='edit_session'),
]

app_name = 'home'
