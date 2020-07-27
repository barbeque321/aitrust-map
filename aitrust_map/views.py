from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def azure_map_project(request):
    return render(request, 'aitrust_map.html', {})

def process_loc(request):
    if request.method == "GET":
        latLngs = request.GET.get('latLngs')
        data = { 'latLngs': latLngs }
    return JsonResponse(data)