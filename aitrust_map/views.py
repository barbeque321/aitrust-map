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
from django.db import connection
import math

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

# def jestWkole(centrum, promien, punkt):
#     if (promien**2) >= ((punkt[0]-centrum[0])**2)+((punkt[1]-centrum[1])**2):
#         return True
#     else:
#         return False

#ylat
def process_loc(request):
    if request.method == "GET":
        lat = request.GET.get('lat') # must be in degrees!
        lng = request.GET.get('lng') # must be in degrees!
        lat = str(lat)
        lng = str(lng)
        lat = lat[:9]
        lng = lng[:9]
        lat = float(lat)
        lng = float(lng)
        rad = request.GET.get('rad') # must be in kilometers!
        rad = round(float(promien), 2)
        theAdressInfo = request.GET.get('theAdressInfo')
        theAdressInfo = str(theAdressInfo)
        R = 6371  # promien Ziemi w kilometrach
        #graniczne punkty okregu (degrees)
        maxLat = lat + math.degrees(rad/R)
        minLat = lat - math.degrees(rad/R)
        maxLon = lng + math.degrees(math.asin(rad/R) / math.cos(math.radians(lat)))
        minLon = lng - math.degrees(math.asin(rad/R) / math.cos(math.radians(lat)))
        # source="epsg:4326"
        # target ="epsg:2180" 
        # transformer = Transformer.from_crs(source, target)
        # lat, lng = transformer.transform(lat, lng)
        # centrum = float(lat), float(lng)
        # promien = request.GET.get('rad')
        # promien = round(float(promien), 2)
    # if "Woj. Pomorskie" in theAdressInfo:
    #     data_place = os.path.join(BASE_DIR,'aitrust_map/pomorskieJSON2180.json')
    #     data_base = json.loads(open(data_place).read())

    # postal_code = []
    # points_sum = 0
    # for keyval in data_base:
    #     if jestWkole(centrum, promien, [float(keyval['Y']), float(keyval['X'])]):
    #         points_sum = points_sum + 1
    #         if keyval['kodPocztowy'] in postal_code:
    #             pass
    #         else:
    #             postal_code.append(keyval['kodPocztowy'])

    # postal_code_sum = len(postal_code)
    # data = { "postal_code": postal_code, "points_sum": points_sum, "postal_code_sum": postal_code_sum
    #     }
        params = { 'lat': lat, 'lon': lng, 'minLat': minLat, 'minLon': minLon, 'maxLat': maxLat, 'maxLon': maxLon, 'rad': rad, 'R': R}
        cursor  = connection.cursor()
        query = "Select Id, kodPocztowy, Lat, Lng, " \
            "acos(sin(:lat)*sin(radians(Lat)) " \
            "+ cos(:lat)*cos(radians(Lat))*cos(radians(Lng)-:lng)) * :R As D " \
            "From ( " \
            "Select Id, kodPocztowy, Lat, Lng " \
            "From pomorskie " \
            "Where Lat Between :minLat And :maxLat" \
            "And Lng Between :minLng And :maxLng" \
            ") As FirstCut " \
            "Where acos(sin(:lat)*sin(radians(Lat)) " \
            "+ cos(:lat)*cos(radians(Lat))*cos(radians(Lng)-:lng)) * :R < :rad " \
            "Order by D"
        cursor.execute(query, params)
        data = cursor.fetchall()


    return JsonResponse(data)



def process_loc2(request):
    if request.method == "GET":
        latLngs = request.GET.get('latLngs')
        data = { 
        "latLngs": latLngs,
        }
    return JsonResponse(data)


