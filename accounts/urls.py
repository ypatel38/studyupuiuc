from django.urls import path
from . import views


urlpatterns = [
    path('', views.temp) #this will be redirected to profile eventually
]
