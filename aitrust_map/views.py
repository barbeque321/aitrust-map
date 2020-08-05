from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
import os
import json
from django.db import connection
import math

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def azure_map_project(request):
    return render(request, 'aitrust_map.html', {})

def process_loc(request):
    if request.method == "GET":
        lat = request.GET.get('lat') # must be in degrees!
        lng = request.GET.get('lng') # must be in degrees!
        lat = str(lat)
        lng = str(lng)
        lat = lat[:9] # unifying the data 
        lng = lng[:9] # unifying the data 
        lat = float(lat)
        lng = float(lng)
        rad = request.GET.get('rad') 
        rad = round(float(rad), 2) # unifying the data
        rad = rad/1000 # must be in kilometers!
        theAdressInfo = request.GET.get('theAdressInfo')
        theAdressInfo = str(theAdressInfo)
        R = 6371  # earth radius in kilometers

        # border points max-min
        # the bounding latitudes are obtained by adding/subtracting the radius from the latitude
        maxLat = lat + math.degrees(rad/R)
        minLat = lat - math.degrees(rad/R)
        maxLng = lng + math.degrees(math.asin(rad/R) / math.cos(math.radians(lat)))
        minLng = lng - math.degrees(math.asin(rad/R) / math.cos(math.radians(lat)))
        
        # dictionary for sql query
        params = { 'lat': lat, 'lng': lng, 'minLat': minLat, 'minLng': minLng, 'maxLat': maxLat, 'maxLng': maxLng, 'rad': rad, 'R': R}
        cursor  = connection.cursor()
        # mysql query
        # initially, the boundary data serves as a pre-filter
        # that the query refers to a limited range of data in the database to make search efficient 
        # then using spherical law of cosines a more accurate circle is drawn and excess points are removed
        query  = """SELECT Id, Lng, Lat, kodPocztowy FROM pomorskie WHERE Lat BETWEEN %(minLat)s AND %(maxLat)s AND Lng BETWEEN %(minLng)s AND %(maxLng)s AND ACOS(SIN(RADIANS(%(lat)s))*SIN(RADIANS(Lat)) + COS(RADIANS(%(lat)s))*COS(RADIANS(Lat))*COS(RADIANS(Lng)-RADIANS(%(lng)s)))*%(R)s < %(rad)s;"""
        cursor.execute(query, params)
        # get mysql data from query
        sql_data = cursor.fetchall()
        
        # getting data from object type and turning arrays into a list
        colnames = ['Id', 'Lng', 'Lat', 'kodPocztowy']
        process_data = {}
        for row in sql_data:
            colindex = 0
            for col in colnames:
                if not col in process_data:
                    process_data[col] = []
                process_data[col].append(row[colindex])
                colindex += 1
        postal_list = process_data['kodPocztowy']
        # calculating the amount of adress points obtained in circle
        points_sum = len(postal_list)
        # removing repetitions from the list and appending unique postal codes
        postal_list_no_repeats = list(dict.fromkeys(postal_list))
        # calculating the amount of postal codes obtained in circle
        postal_code_sum = len(postal_list_no_repeats)

        postal_list_no_repeats_sorted = postal_list_no_repeats.sort()
        postal_code = postal_list_no_repeats_sorted

        data = {"postal_code": postal_code, "points_sum": points_sum, "postal_code_sum": postal_code_sum
        }
        
    return JsonResponse(data)



def process_loc2(request):
    if request.method == "GET":
        latLngs = request.GET.get('latLngs')
        data = { 
        "latLngs": latLngs,
        }
    return JsonResponse(data)


