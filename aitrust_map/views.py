from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from pyproj import Transformer
import matplotlib.pyplot as plt
import pickle
import time
from shapely.geometry import Point, Polygon
from urllib.request import urlopen
import cloudpickle 

# Create your views here.
def azure_map_project(request):
    return render(request, 'aitrust_map.html', {})


def jestWkole(centrum, promien, punkt):
    if (promien**2) >= ((punkt[0]-centrum[0])**2)+((punkt[1]-centrum[1])**2):
        return True
    else:
        return False



def process_loc(request):
    if request.method == "GET":
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        centrum = [lat,lng]
        promien = request.GET.get('rad')
        
    start_time = time.time()
    data_base = cloudpickle.load(urlopen("http://51.195.46.168/dataPL.p", 'rb'))
    mid_time = time.time()
    adresy = []
    adresy_num = 0
    for i, line in enumerate(data_base):
        if i == 0:  # pominiecie nagłówka
            adresy.append(line)
            continue

        coord = line[8].split(' ')
        if jestWkole(centrum, promien, [float(coord[0]), float(coord[1])]):
            adresy.append(line)
            adresy_num += 1
    data = { 
        "liczba_adresow": adresy_num,
        "start_time": start_time,
        "mid_time": mid_time,
        }
    return JsonResponse(data)



def process_loc2(request):
    if request.method == "GET":
        latLngs = request.GET.get('latLngs')
        data = { 
        "latLngs": latLngs,
        }
    return JsonResponse(data)


