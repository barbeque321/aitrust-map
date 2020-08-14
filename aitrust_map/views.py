from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
import os
import json
from django.db import connection
import math
import numpy as np
from scipy.spatial import Delaunay
import networkx as nx
from math import hypot
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
params = [0.75]

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




# ###################################################
# #      DJANGO REQUEST FOR QUICK HULL SHAPE        #
# ###################################################


def draw_polygon(request):
    if request.method == "GET":

        postal_list = request.GET.get('postal_list_to_draw')

        postal_li = list(postal_list.split(", ")) 

        postal_str = ""

        for elem in postal_li:
            postal_str += '"' + elem + '",'

        postal_str = postal_str[:-1]

        # initialise mysql database connection
        cursor  = connection.cursor()
        
        query  = "SELECT Lng, Lat, kodPocztowy FROM pomorskie WHERE kodPocztowy IN ("

        query += postal_str

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

        postal_list_arr = process_data['kodPocztowy']
        total_index = len(postal_list_arr)

        lat_lng_list = {}   
        actual_postal = []
        for num in range(0,total_index):
            index = num
            new_postal = process_data['kodPocztowy'][index]     
            if new_postal in actual_postal:
                new_lat = process_data['Lng'][index]
                new_lng = process_data['Lat'][index]
                lat_lng_list[new_postal].append([new_lat, new_lng])
            else:
                lat_lng_list[new_postal] = []
                actual_postal.append(new_postal)
                new_lat = process_data['Lng'][index]
                new_lng = process_data['Lat'][index]
                lat_lng_list[new_postal].append([new_lat, new_lng])

        hull_points_dict_list = {}
        for key in lat_lng_list:
            points = get_hull_points(lat_lng_list[key])
            hull_points_dict_list[key] = []
            hull_points_dict_list[key].append(points) 

        data = {
        "point_list": point_list, "process_data": process_data, "postal_list": lat_lng_list, "postal_str": hull_points_dict_list
        }
    return JsonResponse(data)


# ###################################################
# #       FUNCTIONS FOR QUICK HULL ALGORITHM        #
# ###################################################

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

# Reterns all points that are 'LEFT' of a line start->end
# In other words the points cluster is divided in half
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
# point is from the line
def distance(start, end, pt): # pt is the point
    x1, y1 = start
    x2, y2 = end
    x0, y0 = pt
    nom = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    denom = ((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5
    result = nom / denom
    return result

# Check if point is 'counter clock wise' to dividing line (lets say on 'left side' of line - depending from line orientation)
def isCCW(start, end, point):
    answer = (end[0] - start[0]) * (point[1] - start[1]) - (end[1] - start[1]) * (point[0] - start[0])
    if answer < 0:
        return True
    else:
        return False



# ###################################################
# # HELPER FUNCTIONS FOR ALPAHA SHAPE MAIN FUNCTION #
# ###################################################

# check if points are in some radius
# earth is spheroid here to be more precise in calculations 

def distance(lat1, lons1, lat2, lons2, rad):
    a = 6378.137  # equitorial radius in km
    b = 6356.752  # polar radius in km

    lat1 = math.radians(lat1)
    lons1 = math.radians(lons1)
    R1 = (((((a ** 2) * math.cos(lat1)) ** 2) + (((b ** 2) * math.sin(lat1)) ** 2)) / (
                (a * math.cos(lat1)) ** 2 + (b * math.sin(lat1)) ** 2)) ** 0.5  # radius of earth at lat1
    x1 = R1 * math.cos(lat1) * math.cos(lons1)
    y1 = R1 * math.cos(lat1) * math.sin(lons1)
    z1 = R1 * math.sin(lat1)

    lat2 = math.radians(lat2)
    lons2 = math.radians(lons2)
    R2 = (((((a ** 2) * math.cos(lat2)) ** 2) + (((b ** 2) * math.sin(lat2)) ** 2)) / (
                (a * math.cos(lat2)) ** 2 + (b * math.sin(lat2)) ** 2)) ** 0.5  # radius of earth at lat2
    x2 = R2 * math.cos(lat2) * math.cos(lons2)
    y2 = R2 * math.cos(lat2) * math.sin(lons2)
    z2 = R2 * math.sin(lat2)

    return ((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2) ** 0.5 < rad

def area_of_polygon_xy(x, y):
    # Calculates the area of an arbitrary polygon given its verticies
    area = 0.0
    for i in range(-1, len(x)-1):
        area += x[i] * (y[i+1] - y[i-1])
    return abs(area) / 2.0

def area_of_polygon_crd(cordinates):
    # Calculates the area of an arbitrary polygon given its verticies
    x = [v[0] for v in cordinates]
    y = [v[1] for v in cordinates]
    return area_of_polygon_xy(x,y)

def sqrt_sum(a, b):
    x = (a[0]-b[0])
    y = (a[1]-b[1])
    return np.sqrt(x*x+y*y)

def shape_to_some_polygons(shape):
    G = nx.Graph()
    allnodes = set()
    for line in shape:
        G.add_nodes_from(line)
        G.add_edge(line[0], line[1])
        allnodes.add(line[0])
        allnodes.add(line[1])

    result = []

    while allnodes:
        node = allnodes.pop()
        new_node = next(iter(G[node]), None)
        if not new_node: continue

        G.remove_edge(node, new_node)
        temp = nx.shortest_path(G, node, new_node)
        for j,t in enumerate(temp):
            if t in allnodes:
                allnodes.remove(t)
        result.append(temp)
    return result

# ###################################################
# #           ALPAHA SHAPE MAIN FUNCTION            #
# ###################################################

def get_alfa_shape_points(pts, alfas=1):
    tri_ind = [(0,1),(1,2),(2,0)]
    tri = Delaunay(pts)
    lenghts = {}
    for s in tri.simplices:
        for ind in tri_ind:
            a = pts[s[ind[0]]]
            b = pts[s[ind[1]]]
            line = (a, b)
            lenghts[line] = sqrt_sum(a, b)

    ls = sorted(lenghts.values())
    mean_length = np.mean(ls)
    mean_length_index = ls.index(next(filter(lambda x: x>=mean_length, ls)))
    magic_numbers = [ls[i] for i in range(mean_length_index, len(ls))]
    magic_numbers[0] = 0
    sum_magic = np.sum(magic_numbers)
    for i in range(2, len(magic_numbers)):
        magic_numbers[i] += magic_numbers[i-1]
    magic_numbers = [m /sum_magic for m in magic_numbers]

    rez = []
    for alfa in alfas:
        i = magic_numbers.index(next(filter(lambda z: z > alfa, magic_numbers), magic_numbers[-1]))
        av_length = ls[mean_length_index+i]
        lines = {}

        for s in tri.simplices:
            used = True
            for ind in tri_ind:
                if lenghts[(pts[s[ind[0]]], pts[s[ind[1]]])] > av_length:
                    used = False
                    break
            if used == False: continue

            for ind in tri_ind:
                i, j = s[ind[0]], s[ind[1]]
                line = (pts[min(i, j)], pts[max(i, j)])
                lines[line] = line in lines

        good_lines = []
        for v in lines:
            if not lines[v]:
                good_lines.append(v)

        result = shape_to_some_polygons(good_lines)
        result.sort(key=area_of_polygon_crd, reverse=True)
        rez.append(result)
    return rez


# ##################################################
# #        DJANGO REQUEST FOR ALPHA SHAPES         #
# ##################################################

def draw_polygon_better(request):
    if request.method == "GET":
        # getting some geo data
        # it will be used later to double check if coordinates of postal codes
        # are correct, if not they will be removed from drawing polygons
        # if all coordinates are wrong postal code will be removed too
        postal_list = request.GET.get('postal_list_to_draw')
        lat_center = request.GET.get('lat') 
        lng_center = request.GET.get('lng') 
        lat_center = str(lat_center)
        lng_center = str(lng_center)
        lat_center = lat_center[:9] # unifying the data 
        lng_center = lng_center[:9] # unifying the data 
        lat_center = float(lat_center)
        lng_center = float(lng_center)
        rad = request.GET.get('rad')
        rad = round(float(rad), 2) # unifying the data 
        rad = rad/1000 # must be in kilometers!
        rad = rad * 2 
        rad = round(float(rad), 2) # unifying the data

        # list of postal codes generated earlier
        postal_li = list(postal_list.split(", ")) 

        # building string of postal codes 
        # each postal code needs to be in quotes 
        postal_str = ""

        # there is ton of unpredicted symbols in database like /, ", ', (), etc.; 
        # also postal codes are misspelled like "0-0000"; this is one of few steps to 
        # clearing this garbage; all symbols are removed from postal code string
        # including "-" sign; then when string is all num only (00000), after the second digit "-" symbol is added
        # also in case ther is none postal code or it is broken beyond repair (not enough digits) it
        # won't be appended to final list 

        for elem in postal_li:
            # this regular expresion '\W == [^a-zA-Z0-9_], pass only numbers, letters and _ sign
            elem = re.sub(r'\W+', '', elem)
            # checking if all that left is a minimal of 5 digits only; remove 00000;
            if len(elem) < 5 or elem.isdigit() == False or elem == "00000":
                pass
            else:
                # adding "-" sign after the second digit
                elem = elem[:2] + "-" + elem[2:]
                # adding quotes and comma; final result is string like -> "00-000",
                postal_str += '"' + elem + '",'


        # remove last char from finall string with all postal codes, which is ','
        # leaving this little comma will generate sql query error
        postal_str = postal_str[:-1]

        # initialise mysql database connection
        cursor  = connection.cursor()
        
        # building mysql query from 3 'parts'
        # the middle part is previously prepared postal codes final string 
        # sql will return lats and langs of all points for every postal code in string
        query  = "SELECT Lng, Lat, kodPocztowy FROM pomorskie WHERE kodPocztowy IN ("

        query += postal_str

        query += ");"

        # execute query
        cursor.execute(query)

        # return mysql data from query
        sql_data = cursor.fetchall()

        # processing returned sql data to form of dictionary
        colnames = ['Lng', 'Lat', 'kodPocztowy']
        process_data = {}
        for row in sql_data:
            colindex = 0
            for col in colnames:
                if not col in process_data:
                    process_data[col] = []
                process_data[col].append(row[colindex])
                colindex += 1

        # geting lenght of array (number of kyes)
        postal_list_arr = process_data['kodPocztowy']
        total_index = len(postal_list_arr)

        lat_lng_list = {}   
        actual_postal = []
        for num in range(0, total_index):
            index = num
            new_postal = process_data['kodPocztowy'][index]
            new_lng = process_data['Lng'][index]
            new_lat = process_data['Lat'][index]  
            if new_postal in actual_postal:
                if distance(lat_center, lng_center, new_lat, new_lng, rad):
                    lat_lng_list[new_postal].append([new_lng, new_lat])
                else:
                    pass
            else:
                if distance(lat_center, lng_center, new_lat, new_lng, rad):
                    lat_lng_list[new_postal] = []
                    actual_postal.append(new_postal)
                    lat_lng_list[new_postal].append([new_lng, new_lat])
                else:
                    pass

        # here real magic happens boys and girls
        # some hardcore trigonometry is called to help
        # I tried KirckPatrick, QuickHall and some other algorithms
        # none of them was precise enough for this problem
        # but they were faster tho

        alfa_shape_points_dict_list = {}
        for key in lat_lng_list:
            actual_list = lat_lng_list[key]
            points_after = []
            for point in actual_list:
                p = (float(point[0]), float(point[1]))
                points_after.append(p)
            if len(points_after) < 5:
                pass
            else:
                points = get_alfa_shape_points(points_after, alfas=params)
                alfa_shape_points_dict_list[key] = []
                alfa_shape_points_dict_list[key].append(points) 

        data = {
        "postal_str": alfa_shape_points_dict_list, "postal_list": points_after, "postal_li": postal_li
        }
    return JsonResponse(data)




















