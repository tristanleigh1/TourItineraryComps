from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.http import HttpResponse, JsonResponse
from django.db.models import Func, F
import logging
import json
from .models import *
import math
from decimal import *


# Create your views here.
#GET: tour/
def index(request):
    return render(request, 'tour/index.html')

def about(request):
    return render(request, 'tour/about.html')

def contact(request):
    return render(request, 'tour/contact.html')

def directions(request):
    return render(request, 'tour/directions.html')

def km_to_lat_lng(km, latitude):
    # 1km = 0.009043 degrees (for latitude)
    KM_TO_DEGREES_LAT = 0.009043
    # 1km = 0.008983 / cos(latitude) (for longitude)
    degrees_lat = km * KM_TO_DEGREES_LAT
    degrees_lng = km / (111.320 * math.cos(math.radians(latitude)))
    return degrees_lat, degrees_lng

def pop_radius(request):
    if request.method == 'GET':
#        name = request.GET.get('name', None)
#        poi_id = request.GET.get('id', None)
        latitude = float(request.GET.get('lat', None))
        longitude = float(request.GET.get('lng', None))
        radius_size = int(request.GET.get('radius', None)) / 1000
        filter_status = int(request.GET.get('filter-status', None))

        categories = []
        if filter_status % 2 != 0:
            categories.append("Restaurants")
        if (filter_status >> 1) % 2 != 0:
            categories.append("Nature")
        if (filter_status >> 2) % 2 != 0:
            categories.append("Activities")
        if (filter_status >> 3) % 2 != 0:
            categories.append("Landmarks")
        if (filter_status >> 4) % 2 != 0:
            categories.append("Museums")

#        if filter_status != 31:
#            raise Exception(filter_status)
#        poi = POI.objects.get(id = poi_id)
#
#        latitude = float(poi.latitude)
#        longitude = float(poi.longitude)
#        city = poi.city

        degrees_lat, degrees_lng = km_to_lat_lng(radius_size, latitude)

        nearby_POI_querySets = []
        for i in range(len(categories)):
            nearby_pois_for_category = POI.objects.filter(category=categories[i], latitude__lte=latitude+degrees_lat, latitude__gte=latitude-degrees_lat, longitude__lte=longitude+degrees_lng, longitude__gte=longitude-degrees_lng)
            nearby_POI_querySets.append(nearby_pois_for_category)

        ##(new_latitude-origin_latitude)^2 + (new_longitude - origin_longitude^2 <= radius^2
#       response_data['poi'] = poi.business_name
        response_data = {}
        response_data['nearby_pois'] = list()
        for nearby_pois in nearby_POI_querySets:
            for nearby_poi in nearby_pois:
                response_data['nearby_pois'].append({'name' : nearby_poi.business_name,
                                                     'latitude' : nearby_poi.latitude,
                                                     'longitude' : nearby_poi.longitude,
                                                     'poi_id' : nearby_poi.id,
                                                     'rating' : nearby_poi.num_stars,
                                                     'category': nearby_poi.category
                                                     })
        return JsonResponse(response_data)
    else:
        return HttpResponse(
                json.dumps({"error":"an error occured."}),
                content_type="application/json"
        )

def get_summary_for_added_point(request):
    if request.method == 'GET':
        poi_id = request.GET.get('id', None)
        query_set = list(POI.objects.filter(id=poi_id))

        response_data = {}
        response_data['summary'] = query_set[0].summary
        return JsonResponse(response_data)
    else:
        return HttpResponse(
                json.dumps({"error":"an error occured."}),
                content_type="application/json"
        )


def calculate_score(current_poi, path_segments, walk_factor, preferences):
    empirical_coefficient = 0.0006
    category = current_poi.category
    popularity = current_poi.popularity
    distance_to_path = float("inf")
    closest_segment = None

    # Cast longitude and latitude to floats
    poi_longitude = float(current_poi.longitude)
    poi_latitude = float(current_poi.latitude)

    # To determine if the POI should be added in the middle of a segment or to the
    # beginning or end of a segment, we'll assume middle for now
    finalWhereInSegment = "middle"
    totalPreferencePoints = 1.0 + float(preferences[0]) + float(preferences[1]) + float(preferences[2]) + float(preferences[3])
    score = float("inf")
    if current_poi.category == 'Museums':
        taste = float(preferences[0])/totalPreferencePoints
    elif current_poi.category == 'Landmarks':
        taste = float(preferences[1])/totalPreferencePoints
    elif current_poi.category == 'Activities':
        taste = float(preferences[2])/totalPreferencePoints
    else:
        taste = float(preferences[3])/totalPreferencePoints

    walk_factor = float(walk_factor) * (3.0/10.0)

    # Loop through every existing segment to find the closest one to add the new POI to
    for i in range(len(path_segments)):
        seg = path_segments[i]
        # Calculate closest line (Remember: latitude is x direction, longitude is y)
        x1, x2 = float(seg[0].latitude), float(seg[1].latitude)
        y1, y2 = float(seg[0].longitude), float(seg[1].longitude)
        rise = y2 - y1
        run = x2 - x1

        if rise == 0:
            # Horizontal line
            distance_to_segment = abs(y1 - poi_longitude)
            whereInSegment = "middle"
        elif run == 0:
            # Vertical line
            distance_to_segment = abs(x1 - poi_latitude)
            whereInSegment = "middle"
        else:
            # Calculate slopes and y-intercepts
            slope = rise / run
            orthogonal_slope = (run / rise) * -1.0
            y_int = y1 - (slope * x1)
            orthogonal_y_int = poi_longitude - (orthogonal_slope * poi_latitude)

            # Find where lines intersect
            intersect_x = (orthogonal_y_int - y_int) / (slope - orthogonal_slope)
            intersect_y = (slope * intersect_x) + y_int

            distance_start_to_end = ((y2 - y1)**2 + (x2-x1)**2)**(1/2)
            distance_start_to_POI = ((intersect_y - y1)**2 + (intersect_x-x1)**2)**(1/2)
            distance_POI_to_end = ((y2 - intersect_y)**2 + (x2-intersect_x)**2)**(1/2)

            # Check if intersection is part of segment
            if abs(distance_start_to_POI + distance_POI_to_end - distance_start_to_end) <= 0.000001:
                # Distance formula
                distance_to_segment = math.sqrt((intersect_x - poi_latitude)**2 + (intersect_y - poi_longitude)**2)
                whereInSegment = "middle"
            else:
                distance_to_start = math.sqrt((x1 - poi_latitude)**2 + (y1 - poi_longitude)**2)
                distance_to_end = math.sqrt((x2 - poi_latitude)**2 + (y2 - poi_longitude)**2)
                if distance_to_start < distance_to_end:
                    distance_to_segment = distance_to_start
                   # if i > 0
                    if seg[0].category != "Origin":
                        whereInSegment = "begin"
                    else:
                        whereInSegment = "middle"
                else:
                    distance_to_segment = distance_to_end
                    if seg[1].category != "Destination":
                        whereInSegment = "end"
                    else:
                        whereInSegment = "middle"


       # Update the smallest distance
        if distance_to_segment < distance_to_path:
            distance_to_path = distance_to_segment
            closest_segment = seg
            finalWhereInSegment = whereInSegment
        if distance_to_segment == distance_to_path:
            #logging.info("TWO SEGMENTS ARE SAME DISTANCE")
            pass

    # Calculate the score
    score = float(distance_to_path) - empirical_coefficient * float(popularity) * taste * walk_factor


    return score, closest_segment, finalWhereInSegment

def update_segments(current_segments, new_poi, segment_to_add_to, whereInSegment):
    seg_index = current_segments.index(segment_to_add_to)
    # if len(current_segments) == 2:
    #     raise Exception(whereInSegment)
    if whereInSegment == "end":
    #logging.info("Updating segments. Adding %s between segment %i and segment %i." %(str(new_poi), seg_index, seg_index + 1))
        new_segment = (current_segments[seg_index][1], new_poi)
        current_segments[seg_index + 1] = (new_poi, current_segments[seg_index + 1][1])
        current_segments.insert(seg_index+1, new_segment)

    elif whereInSegment == "begin":
        new_segment = (new_poi, current_segments[seg_index][0])
        current_segments[seg_index - 1] = (current_segments[seg_index - 1][0], new_poi)
        current_segments.insert(seg_index, new_segment)
    else:
        new_segment = (current_segments[seg_index][0], new_poi)
        current_segments[seg_index] = (new_poi, current_segments[seg_index][1])
        current_segments.insert(seg_index, new_segment)

def find_next_poi(poi_list, path_segments, walk_factor, preferences):
    poi_to_add = None
    seg_to_add_to = None
    min_score = float("inf")
    finalWhereInSegment = ""
    for poi in poi_list:
        if poi.category == 'Restaurants':
            continue
        if poi.business_name == path_segments[0][0].business_name:
            continue
        if poi.business_name == path_segments[len(path_segments)-1][1].business_name:
            continue
        score, segment, whereInSegment = calculate_score(poi, path_segments, walk_factor, preferences)
        if score < min_score:
            poi_to_add = poi
            min_score = score
            seg_to_add_to = segment
            finalWhereInSegment = whereInSegment
    update_segments(path_segments, poi_to_add, seg_to_add_to, finalWhereInSegment)
   # if poi_to_add.business_name == 'Museo Nacional del Prado':
    #    raise Exception('here')
    return poi_to_add

def create_path(total_pois, start, end, walk_factor, preferences, num_destinations):
    MAX_POIS = int(num_destinations)
    # path_segments is a list of pairs of points
    path_segments = [(start, end)]
    path_pois = []
    total_pois = list(total_pois)

   # count = 0
    for poi in total_pois:
        if abs(poi.latitude - start.latitude) < .0015 and abs(poi.longitude - start.longitude) < .0015:
            total_pois.remove(poi)
  #          count = count + 1
        if abs(poi.latitude - end.latitude) < .0015 and abs(poi.longitude - end.longitude) < .0015:
            total_pois.remove(poi)
 #           count = count + 1

#    raise Exception(count)

    # Check if start or end are POIs, if so remove from list

    # given a start and end address (which we take as lat lng):
    # 1. Check if it's a POI
    # 2. If so, remove POI from list and make start point it's POI object
    # 3. If not, deal with starting with an address, not a POI

    while len(path_pois) < MAX_POIS:
        poi = find_next_poi(total_pois, path_segments, walk_factor, preferences)
        #logging.info("adding poi " + str(poi))
        path_pois.append(poi)
        # Not sure if remove is correct
        total_pois.remove(poi)

    final_path_pois = []
    for i in range(len(path_segments)-1):
        final_path_pois.append(path_segments[i][1])
    return final_path_pois

#GET: tour/map/
def map(request):

    # origin = get_object_or_404(POI, pk=2569)
    # destination = get_object_or_404(POI, pk=2611)

    # Form values
    mode = request.GET['mode']
    if (mode == "start-to-end"):
        return startToEnd(request)
    elif (mode == "exploratory"):
        return exploratory(request)


def exploratory(request):
    city = request.GET['city']
    start_coords = request.GET['startCoords']

    origin = POI()
    origin.latitude = Decimal(start_coords[1:-1].split(", ")[0])
    origin.longitude = Decimal(start_coords[1:-1].split(", ")[1])
    origin.business_name = request.GET['startDestination'].split(',')[0]
    origin.category = "Origin"
    destination = get_object_or_404(POI, pk=2569)

    context = { 'mode': "exploratory",
                'origin': origin,
                'destination': destination,
                'city': city,
                'start_coords': start_coords}
    return render(request, 'tour/map.html', context)

def startToEnd(request):
    city = request.GET['city']
    start_coords = request.GET['startCoords']
    end_coords = request.GET['endCoords']
    start_address = request.GET['startAddress']
    end_address = request.GET['endAddress']
    num_destinations = request.GET['points']
    walk_factor = request.GET['miles']
    museum_preference = request.GET['museums']
    landmark_preference = request.GET['landmarks']
    activity_preference = request.GET['activities']
    nature_preference = request.GET['parks']

    origin = POI()
    destination = POI()
    origin.latitude = Decimal(start_coords[1:-1].split(", ")[0])
    origin.longitude = Decimal(start_coords[1:-1].split(", ")[1])
    origin.business_name = request.GET['startDestination'].split(',')[0]
    origin.category = "Origin"
    origin.address = start_address

    destination.latitude = Decimal(end_coords[1:-1].split(", ")[0])
    destination.longitude = Decimal(end_coords[1:-1].split(", ")[1])
    destination.business_name = request.GET['endDestination'].split(',')[0]
    destination.category = "Destination"
    destination.address = end_address

    preferences = [museum_preference, landmark_preference, activity_preference, nature_preference]

    poi_list = POI.objects.filter(city=city)
    final_path = create_path(poi_list, origin, destination, walk_factor, preferences, num_destinations)

    context = { #'category_dict': category_dict,
                'mode': 'startToEnd',
                'poi_list': final_path,
                'origin': origin,
                'destination': destination,
                'city': city}
    return render(request, 'tour/map.html', context)
