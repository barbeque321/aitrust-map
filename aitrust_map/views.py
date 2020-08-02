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

# def punktyWpolygonie(data, polygon):

#     poly = Polygon(polygon)
#     adresy = []
#     for i, line in enumerate(data):

#         if i == 0:  # pominiecie nagłówka
#             adresy.append(line)
#             continue

#         coord = line[8].split(' ')
#         p = Point(float(coord[0]), float(coord[1]))
#         # print(i)
#         if p.within(poly):
#             adresy.append(line)
#             #print(i, ' zapisano')
#     return adresy

# def transformPoly(polygon,source="epsg:3857",target ="epsg:2180" ):

#     transformer = Transformer.from_crs(source, target)
#     poly = []
#     for point in polygon:
#         poly.append(transformer.transform(*point))

#     return poly


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
        theAdressInfo = request.GET.get('theAdressInfo')
        theAdressInfo = str(theAdressInfo)
        lat = float(lat)
        lng = float(lng)
        source="epsg:4326"
        target ="epsg:2180" 
        transformer = Transformer.from_crs(source, target)
        lat, lng = transformer.transform(lat, lng)
        lat = str(lat)
        lng = str(lng)
        lat = lat[:16]
        lng = lng[:16]    
        centrum = float(lat), float(lng)
        promien = request.GET.get('rad')
        promien = round(float(promien), 2)


        
    
    data_place = os.path.join(BASE_DIR,'aitrust_map/all_states.json')
    data_base = json.loads(open(data_place).read())
    

    postal_code = []
    points_sum = 0
    for keyval in data_base:
        if jestWkole(centrum, promien, [float(keyval['Y']), float(keyval['X'])]):
            points_sum = points_sum + 1
            if keyval['kodPocztowy'] in postal_code:
                pass
            else:
                postal_code.append(keyval['kodPocztowy'])

    postal_code_sum = len(postal_code)
    data = { "postal_code": postal_code, "points_sum": points_sum, "postal_code_sum": postal_code_sum
        }
    return JsonResponse(data)



def process_loc2(request):
    if request.method == "GET":
        latLngs = request.GET.get('latLngs')
        data = { 
        "latLngs": latLngs,
        }
    return JsonResponse(data)


