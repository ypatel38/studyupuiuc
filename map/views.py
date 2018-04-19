from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
class MapView(TemplateView):
    template_name = 'map/map.html'

    def get(self, request):
        return HttpResponse("Map")

    def post(self, request):
        pass
