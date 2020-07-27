from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse


# Create your views here.
def azure_map_project(request):
    return render(request, 'aitrust_map.html', {})

def process_loc(request):
    if request.method == "GET":
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        rad = request.GET.get('rad')
        data = { 
        "lat": lat,
        "lng": lng, 
        "rad": rad,
        }
    return JsonResponse(data)

def process_loc2(request):
    if request.method == "GET":
        latLngs = request.GET.get('latLngs')
        data = { 
        "latLngs": latLngs,
        }
    return JsonResponse(data)

