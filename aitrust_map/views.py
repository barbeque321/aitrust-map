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
        "difference_postal_num": difference_postal_num, "differene_points_num": differene_points_num, "postal_list_no_repeats": postal_list_no_repeats}
        
    return JsonResponse(data)



def process_loc2(request):
    if request.method == "GET":
        latLngs = request.GET.get('latLngs')
        data = { 
        "latLngs": latLngs,
        }
    return JsonResponse(data)

def draw_polygon(request):
    if request.method == "GET":

        postal_array = request.GET.get('postal_list_to_draw')
        postal_list = postal_array

        # initialise mysql database connection
        cursor  = connection.cursor()
        
        query  = "SELECT Lng, Lat, kodPocztowy FROM pomorskie WHERE kodPocztowy IN ("

        query += postal_list

        query += ");"

        # execute first query
        cursor.execute(query)

        # return mysql data from query
        sql_data = cursor.fetchall()

        colnames = ['Lng', 'Lat', 'kodPocztowy']
        process_data = {}
        for row in sql_data:
            colindex = 0
            for col in colnames:
                if not col in process_data:
                    process_data[col] = []
                process_data[col].append(row[colindex])
                colindex += 1

        # postal_code_to_draw = request.GET.get('postal_code_to_draw')
        listPts = ([15.413973422184, 51.0212037670241],
                  [15.4332214925837, 51.0799312750014],
                  [15.4050494551369, 51.0344862705881],
                  [15.4414447200904, 51.044045040425],
                  [15.4194705970584, 51.0320655974664],
                  [15.4199662699941, 51.0316117568038],
                  [15.433644655413, 51.0294399180875],
                  [15.4385066561904, 51.0805483023349],
                  [15.4132619454792, 51.0285069795709],
                  [15.4576386554641, 50.9867400945641],
                  [15.4220407377152, 51.0316597560996],
                  [15.4014502254017, 51.0299148164245],
                  [15.4221420936325, 51.0619805783075],
                  [15.4151390895601, 51.0225180901085],
                  [15.4198609882746, 51.0178453391329],
                  [15.4197830789713, 51.0185619946637],
                  [15.4201531445335, 51.0189519170405],
                  [15.4248930331689, 51.0341888130886],
                  [15.4345825939314, 51.0386060629985],
                  [15.3904915874004, 51.0186226505184],
                  [15.3986676965896, 51.0057241223047],
                  [15.4352049186695, 51.0476605016435],
                  [15.4394653824091, 51.021500652971],
                  [15.4399585048548, 50.9858833271328],
                  [15.4221460128028, 51.058306470713],
                  [15.4004136699689, 51.0311436908024],
                  [15.4064553007771, 51.0278138175592],
                  [15.408985526436, 51.0288722422194],
                  [15.4455943752375, 50.9835381294996],
                  [15.4457446017111, 50.9839807988255],
                  [15.4479149995378, 50.9848441966871])
        point_list = get_hull_points(listPts)
        data = {
        "point_list": point_list, "process_data": process_data, "postal_list": postal_list
        }
    return JsonResponse(data)

# main execution body of getting quickhall points set for polygon
def get_hull_points(listPts):
    min, max = get_min_max_x(listPts)
    hullpts = quickhull(listPts, min, max)
    hullpts = hullpts + quickhull(listPts, max, min)
    return hullpts

# Does the sorting for the quick hull sorting algorithm
def quickhull(listPts, min, max):
    left_of_line_pts = get_points_left_of_line(min, max, listPts)
    ptC = point_max_from_line(min, max, left_of_line_pts)
    if len(ptC) < 1:
        return [max]
    hullPts = quickhull(left_of_line_pts, min, ptC)
    hullPts = hullPts + quickhull(left_of_line_pts, ptC, max)
    return hullPts

# Reterns all points that a LEFT of a line start->end
def get_points_left_of_line(start, end, listPts):
    pts = []
    for pt in listPts:
        if isCCW(start, end, pt):
            pts.append(pt)
    return pts

# Returns the maximum point from a line start->end
def point_max_from_line(start, end, points):
    max_dist = 0
    max_point = []
    for point in points:
        if point != start and point != end:
            dist = distance(start, end, point)
            if dist > max_dist:
                max_dist = dist
                max_point = point
    return max_point

def get_min_max_x(list_pts):
    min_x = float('inf')
    max_x = 0
    min_y = 0
    max_y = 0

    for x, y in list_pts:
        if x < min_x:
            min_x = x
            min_y = y
        if x > max_x:
            max_x = x
            max_y = y
    return [min_x, min_y], [max_x, max_y]

# Given a line of start->end, will return the distance that
# point, pt, is from the line.
def distance(start, end, pt): # pt is the point
    x1, y1 = start
    x2, y2 = end
    x0, y0 = pt
    nom = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    denom = ((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5
    result = nom / denom
    return result

# Check is point counter clock wise to line (on left side depending from line orientation)
def isCCW(start, end, point):
    answer = (end[0] - start[0]) * (point[1] - start[1]) - (end[1] - start[1]) * (point[0] - start[0])
    if answer < 0:
        return True
    else:
        return False










