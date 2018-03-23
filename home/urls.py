from django.urls import path
from home.views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
]

app_name = 'home'
