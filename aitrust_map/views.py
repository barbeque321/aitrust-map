from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from pyproj import Transformer
import matplotlib.pyplot as plt
import pickle
import time
from shapely.geometry import Point, Polygon
import os
import json


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Create your views here.
def azure_map_project(request):
    return render(request, 'aitrust_map.html', {})


def jestWkole(centrum, promien, punkt):
    if (promien**2) >= ((punkt[0]-centrum[0])**2)+((punkt[1]-centrum[1])**2):
        return True
    else:
        return False


#ylat
def process_loc(request):
    if request.method == "GET":
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        lat = str(lat)
        lng = str(lng)
        centrum = [lat,lng]
        promien = request.GET.get('rad')
    
    data_place = os.path.join(BASE_DIR,'aitrust_map/pomorskieJSON.json')
    data_base = json.loads(open(data_place).read())
    
    postal_codes = []
    for keyval in data_base:
        if (lat == keyval['Y']) and (lng == keyval['X']):
            postal_codes.append(keyval['KodPocztowy'])
        else:
            pass 
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
    data = { "promien": postal_codes, "centrum": centrum
        }
    return JsonResponse(data)



def process_loc2(request):
    if request.method == "GET":
        latLngs = request.GET.get('latLngs')
        data = { 
        "latLngs": latLngs,
        }
    return JsonResponse(data)


