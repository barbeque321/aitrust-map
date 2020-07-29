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
import joblib
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
        start_time = time.time()
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        centrum = [lat,lng]
        promien = request.GET.get('rad')
    
    # data_place = os.path.join(BASE_DIR,'aitrust_map/dataPL.p')
    # data_base = pickle.load(open(data_place, 'rb'))
    # adresy = []
    # adresy_num = 0
    # for i, line in enumerate(data_base):
    #     if i == 0:  # pominiecie nagłówka
    #         adresy.append(line)
    #         continue

    #     coord = line[8].split(' ')
    #     if jestWkole(centrum, promien, [float(coord[0]), float(coord[1])]):
    #         adresy.append(line)
    #         adresy_num += 1
    #         break
    end_time = time.time()
    data = { "generated_info": [start_time, promien, lat, lng, centrum, end_time]

        }
    return JsonResponse(data)



def process_loc2(request):
    if request.method == "GET":
        latLngs = request.GET.get('latLngs')
        data = { 
        "latLngs": latLngs,
        }
    return JsonResponse(data)


