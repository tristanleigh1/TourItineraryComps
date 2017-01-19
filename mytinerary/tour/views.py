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

def pop_radius(request):
    if request.method == 'GET':
        name = request.GET.get('name', None)
        poi_id = request.GET.get('id', None)
        response_data = {"name": name, "id": poi_id}
        
        poi = POI.objects.get(id = poi_id)
        
        latitude = float(poi.latitude)
        longitude = float(poi.longitude)
        city = poi.city
        radius = 0.004 ##nead to consider curve of earth
        nearby_pois = POI.objects.filter(city = city).filter(latitude__lte=latitude+radius, latitude__gte=latitude-radius, longitude__lte=longitude+radius, longitude__gte=longitude-radius) ##(new_latitude-origin_latitude)^2 + (new_longitude - origin_longitude^2 <= radius^2
        response_data['poi'] = poi.business_name
        response_data['nearby_pois'] = list()
        for poi in nearby_pois:
            response_data['nearby_pois'].append({'name' : poi.business_name,
                                                 'latitude' : poi.latitude,
                                                 'longitude' : poi.longitude,
                                                 'poi_id' : poi.id
                                                 })
        return JsonResponse(response_data)
    else:
        return HttpResponse(
                json.dumps({"error":"an error occured."}),
                content_type="application/json"
        )

def calculate_score(current_poi, path_segments, walk_factor, preferences):
    empirical_coefficient = 0.0002
    category = current_poi.category
    popularity = current_poi.popularity
    distance_to_path = float("inf")
    closest_segment = None
    # To determine if the POI should be added in the middle of a segment or to the 
    # beginning or end of a segment, we'll assume middle for now
    whereInSegment = "middle"
    score = float("inf")
    if current_poi.category == 'Museums':
        taste = float(preferences[0]) * (1.0/4.0)
    elif current_poi.category == 'Landmarks':
        taste = float(preferences[1]) * (1.0/4.0)
    elif current_poi.category == 'Activities':
        taste = float(preferences[2]) * (1.0/4.0)
    else:
        taste = float(preferences[3]) * (1.0/4.0)

    walk_factor = float(walk_factor) * (3.0/10.0)

    # Loop through every existing segment to find the closest one to add the new POI to
    for i in range(len(path_segments)):
        seg = path_segments[i]
        # Calculate closest line (Remember: latitude is x direction, longitude is y)
        x1, x2 = seg[0].latitude, seg[1].latitude
        y1, y2 = seg[0].longitude, seg[1].longitude
        rise = y2 - y1
        run = x2 - x1

        if rise == 0:
            # Horizontal line
            distance_to_segment = abs(y1 - current_poi.longitude)
        elif run == 0:
            # Vertical line
            distance_to_segment = abs(x1 - current_poi.latitude)
        else:
            # Calculate slopes and y-intercepts
            slope = rise / run
            orthogonal_slope = slope * -1
            y_int = y1 - (slope * x1)
            orthogonal_y_int = current_poi.longitude - (orthogonal_slope * current_poi.latitude)

            # Find where lines intersect
            intersect_x = (orthogonal_y_int - y_int) / (2 * slope)
            intersect_y = (slope * intersect_x) + y_int

            # Check if intersection is part of segment
            if x1 <= intersect_x and intersect_x <= x2 and y1 <= intersect_y and intersect_y <= y2:
                # Distance formula
                distance_to_segment = math.sqrt((intersect_x - current_poi.latitude)**2 + (intersect_y - current_poi.longitude)**2)
                whereInSegment = "middle"
            else:
                distance_to_start = math.sqrt((x1 - current_poi.latitude)**2 + (y1 - current_poi.longitude)**2)
                distance_to_end = math.sqrt((x2 - current_poi.latitude)**2 + (y2 - current_poi.longitude)**2)
                if distance_to_start < distance_to_end:
                    distance_to_segment = distance_to_start
                    if i > 0:
                        whereInSegment = "begin"
                    else:
                        whereInSegment = "middle"
                else:
                    distance_to_segment = distance_to_end
                    if i < len(path_segments)-1:
                        whereInSegment = "end"
                    else:
                        whereInSegment = "middle"


        # Update the smallest distance
        if distance_to_segment < distance_to_path:
            distance_to_path = distance_to_segment
            closest_segment = seg
        if distance_to_segment == distance_to_path:
            #logging.info("TWO SEGMENTS ARE SAME DISTANCE")
            pass

    # Calculate the score
    score = float(distance_to_path) - empirical_coefficient * float(popularity) * taste * walk_factor

    return score, closest_segment, whereInSegment

def update_segments(current_segments, new_poi, segment_to_add_to, whereInSegment):
    seg_index = current_segments.index(segment_to_add_to)
    if whereInSegment == "middle":
    #logging.info("Updating segments. Adding %s between segment %i and segment %i." %(str(new_poi), seg_index, seg_index + 1))
        new_segment = (current_segments[seg_index][0], new_poi)
        current_segments[seg_index] = (new_poi, current_segments[seg_index][1])
        current_segments.insert(seg_index, new_segment)
    elif whereInSegment == "begin":
        current_segments[seg_index - 1] = (current_segments[seg_index - 1][0], new_poi)
        new_segment = (new_poi, current_segments[seg_index][0])
        current_segments.insert(seg_index, new_segment)
    else:
        current_segments[seg_index + 1] = (new_poi, current_segments[seg_index + 1][1])
        new_segment = (current_segments[seg_index][1], new_poi)
        current_segments.insert(seg_index+1, new_segment)

def find_next_poi(poi_list, path_segments, walk_factor, preferences):
    poi_to_add = None
    seg_to_add_to = None
    min_score = float("inf")
    whereInSegment = ""
    for poi in poi_list:
        if poi.category == 'Restaurants':
            continue
        score, segment, whereInSegment = calculate_score(poi, path_segments, walk_factor, preferences)
        if score < min_score:
            poi_to_add = poi
            min_score = score
            seg_to_add_to = segment

    update_segments(path_segments, poi_to_add, seg_to_add_to, whereInSegment)

    return poi_to_add

def create_path(total_pois, start, end, walk_factor, preferences, num_destinations):
    MAX_POIS = int(num_destinations)
    # path_segments is a list of pairs of points
    path_segments = [(start, end)]
    path_pois = []
    total_pois = list(total_pois)

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
    city = request.GET['city']
    start_coords = request.GET['startCoords']
    end_coords = request.GET['endCoords']
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
    origin.business_name = "Origin"
    origin.category = "Museums"

    destination.latitude = Decimal(end_coords[1:-1].split(", ")[0])
    destination.longitude = Decimal(end_coords[1:-1].split(", ")[1])
    destination.business_name = "Destination"
    destination.category = "Museums"

    preferences = [museum_preference, landmark_preference, activity_preference, nature_preference]

    poi_list = POI.objects.filter(city=city)
    final_path = create_path(poi_list, origin, destination, walk_factor, preferences, num_destinations)

    context = { #'category_dict': category_dict,
                'poi_list': final_path,
                'origin': origin,
                'destination': destination,
                'city': city,
                'start_coords': start_coords,
                'end_coords': end_coords}
    return render(request, 'tour/map.html', context)
