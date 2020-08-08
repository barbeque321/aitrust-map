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
        rad = round(float(rad), 2) # unifying the data
        rad_up_10 = rad * 1.1 # radius + 10%
        rad_up_10 = round(float(rad_up_10), 2) # unifying the data
        theAdressInfo = request.GET.get('theAdressInfo')
        theAdressInfo = str(theAdressInfo)
        R = 6371  # earth radius in kilometers

        # border points max-min
        # the bounding latitudes are obtained by adding/subtracting the radius from the latitude
        maxLat = lat + math.degrees(rad/R)
        minLat = lat - math.degrees(rad/R)
        maxLng = lng + math.degrees(math.asin(rad/R) / math.cos(math.radians(lat)))
        minLng = lng - math.degrees(math.asin(rad/R) / math.cos(math.radians(lat)))

        # border points max-min + 10%
        maxLat_up_10 = lat + math.degrees(rad_up_10/R)
        minLat_up_10 = lat - math.degrees(rad_up_10/R)
        maxLng_up_10 = lng + math.degrees(math.asin(rad_up_10/R) / math.cos(math.radians(lat)))
        minLng_up_10 = lng - math.degrees(math.asin(rad_up_10/R) / math.cos(math.radians(lat)))

        # initialise mysql database connection
        cursor  = connection.cursor()

        # dictionary for first sql query
        params = { 'lat': lat, 'lng': lng, 'minLat': minLat, 'minLng': minLng, 'maxLat': maxLat, 'maxLng': maxLng, 'rad': rad, 'R': R }
        
        # mysql first query
        # initially, the boundary data serves as a pre-filter
        # that the query refers to a limited range of data in the database to make search efficient 
        # then using spherical law of cosines a more accurate circle is drawn and excess points are removed
        query  = """SELECT Id, Lng, Lat, kodPocztowy FROM pomorskie WHERE Lat BETWEEN %(minLat)s AND %(maxLat)s AND Lng BETWEEN %(minLng)s AND %(maxLng)s AND ACOS(SIN(RADIANS(%(lat)s))*SIN(RADIANS(Lat)) + COS(RADIANS(%(lat)s))*COS(RADIANS(Lat))*COS(RADIANS(Lng)-RADIANS(%(lng)s)))*%(R)s < %(rad)s;"""

        # execute first query
        cursor.execute(query, params)

        # return mysql data from query
        sql_data = cursor.fetchall()

        # second query is all the same but the radius which is 10% larger
        params_up_10 = { 'lat': lat, 'lng': lng, 'minLat_up_10': minLat_up_10, 'minLng_up_10': minLng_up_10, 'maxLat_up_10': maxLat_up_10, 'maxLng_up_10': maxLng_up_10, 'rad_up_10': rad_up_10, 'R': R }
        query_up_10  = """SELECT Id, Lng, Lat, kodPocztowy FROM pomorskie WHERE Lat BETWEEN %(minLat_up_10)s AND %(maxLat_up_10)s AND Lng BETWEEN %(minLng_up_10)s AND %(maxLng_up_10)s AND ACOS(SIN(RADIANS(%(lat)s))*SIN(RADIANS(Lat)) + COS(RADIANS(%(lat)s))*COS(RADIANS(Lat))*COS(RADIANS(Lng)-RADIANS(%(lng)s)))*%(R)s < %(rad_up_10)s;"""
        cursor.execute(query_up_10, params_up_10)
        sql_data_up_10 = cursor.fetchall()
        
        # getting data from object type and turning arrays into a list from first query
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
        separator = ', '
        final_postal_string = separator.join(postal_list_no_repeats) 
        # calculating the amount of postal codes obtained in circle
        postal_code_sum = len(postal_list_no_repeats)

        # getting data from object type and turning arrays into a list from second query
        colnames = ['Id', 'Lng', 'Lat', 'kodPocztowy']
        process_data_up_10 = {}
        for row in sql_data_up_10:
            colindex = 0
            for col in colnames:
                if not col in process_data_up_10:
                    process_data_up_10[col] = []
                process_data_up_10[col].append(row[colindex])
                colindex += 1
        postal_list_up_10 = process_data_up_10['kodPocztowy']
        # calculating the amount of adress points obtained in circle with radius 10% larger
        points_sum_up_10 = len(postal_list_up_10)
        # removing repetitions from the list and appending unique postal codes
        postal_list_no_repeats_up_10 = list(dict.fromkeys(postal_list_up_10))
        # calculating the amount of postal codes obtained in circle with radius 10% larger
        postal_code_sum_up_10= len(postal_list_no_repeats_up_10)


        # counting difference in postal_codes number and adresses number beetween two queries 
        difference_postal_num = postal_code_sum_up_10 - postal_code_sum
        differene_points_num = points_sum_up_10 - points_sum

        # building dictionary for JsonResponse
        data = {"postal_code": final_postal_string, "points_sum": points_sum, "postal_code_sum": postal_code_sum,
        "points_sum_up_10": points_sum_up_10, "postal_code_sum_up_10": postal_code_sum_up_10, "rad": rad, "rad_up_10": rad_up_10,
        "difference_postal_num": difference_postal_num, "differene_points_num": differene_points_num}
        
    return JsonResponse(data)



def process_loc2(request):
    if request.method == "GET":
        latLngs = request.GET.get('latLngs')
        data = { 
        "latLngs": latLngs,
        }
    return JsonResponse(data)


