from django.shortcuts import render
from django.http import HttpResponse #delete later
from django.db import connection, transaction #for sql

# Create your views here.

#this will be the view for the homepage
def temp(request):
    '''cursor = connection.cursor()
    cursor.execute("DROP TABLE test")
    row = cursor.fetchone()
    cursor.close()'''
    return HttpResponse("hi")
 
