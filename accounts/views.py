from django.shortcuts import render, HttpResponse

# Create your views here.
def testview(request):
    return HttpResponse('Test')
