from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.http import HttpResponse
from .models import *
import math

# Create your views here.
#GET: tour/
def index(request):
    return render(request, 'tour/index.html')

def about(request):
    html = "<html><body>A Carleton College comps project created by "
    html += "Caleb Braun, Hailey Jones, Tristan Leigh, and Jonah Tuchow."
    html += "<br><a href='/tour/'>Back</a></html></body>"
    return HttpResponse(html)

def contact(request):
    html = "<html><body><h2>Contact</h2>Please only contact us by snail mail.<br><br>"
    html += "Caleb Braun<br>300 North College St.<br>Northfield, MN 55057</html></body>"
    html += "<br><br><a href='/tour/'>Back</a></html></body>"
    return HttpResponse(html)

def calculate_score(current_poi, path_segments, walk_factor, preferences):
    empirical_coefficient = 0.0002
    category = current_poi.category
    popularity = current_poi.popularity
    distance_to_path = float("inf")
    closest_segment = None
    score = float("inf")
    if current_poi.category == 'Museums':
        taste = float(preferences[0])
    elif current_poi.category == 'Landmarks':
        taste = float(preferences[1])
    elif current_poi.category == 'Activities':
        taste = float(preferences[2])
    else:
        taste = float(preferences[3])
    print(walk_factor)
    walk_factor = float(walk_factor) * (3.0/10.0)

    for seg in path_segments:
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
            else:
                distance_to_start = math.sqrt((x1 - current_poi.latitude)**2 + (y1 - current_poi.longitude)**2)
                distance_to_end = math.sqrt((x2 - current_poi.latitude)**2 + (y2 - current_poi.longitude)**2)
                distance_to_segment = min(distance_to_start, distance_to_end)

        # Update the smallest distance
        if distance_to_segment < distance_to_path:
            distance_to_path = distance_to_segment
            closest_segment = seg

    # Calculate the score
    score = float(distance_to_path) - empirical_coefficient * float(popularity) * taste * walk_factor

    return score, closest_segment

def update_segments(current_segments, new_poi, segment_to_add_to):
    seg_index = current_segments.index(segment_to_add_to)
    new_segment = (current_segments[seg_index][0], new_poi)
    current_segments[seg_index] = (new_poi, current_segments[seg_index][1])
    current_segments.insert(seg_index, new_segment)

def find_next_poi(poi_list, path_segments, slider_val, preferences):
    poi_to_add = None
    segment = None
    min_score = float("inf")
    for poi in poi_list:
        if poi.category == 'Restaurants':
            continue
        score, segment = calculate_score(poi, path_segments, slider_val, preferences)
        if score < min_score:
            poi_to_add = poi
            min_score = score

    update_segments(path_segments, poi_to_add, segment)

    return poi_to_add

def create_path(total_pois, start, end, slider_val, preferences):
    MAX_POIS = 8
    # path_segments is a list of pairs of points
    path_segments = [(start, end)]
    path_pois = []
    total_pois = list(total_pois)

    while len(path_pois) < MAX_POIS:
        poi = find_next_poi(total_pois, path_segments, slider_val, preferences)
        path_pois.append(poi)
        # Not sure if remove is correct
        total_pois.remove(poi)

    return path_pois

#GET: tour/map/
def map(request):

    number = 0
    # category_dict = {}
    # for poi in poi_list:
    #     categories = POI.objects.values_list('category', flat=True).filter(id = poi.id)
    #     category_dict[poi.id] = categories

    origin = get_object_or_404(POI, pk=2569)
    destination = get_object_or_404(POI, pk=2610)

    # Caleb's tests
    city = request.GET['city']
    start_coords = request.GET['startCoords']
    end_coords = request.GET['endCoords']
    slider_val = request.GET['points']
    museum_preference = request.GET['museums']
    landmark_preference = request.GET['landmarks']
    activity_preference = request.GET['activities']
    nature_preference = request.GET['parks']
    
    preferences = [museum_preference, landmark_preference, activity_preference, nature_preference]
    
    poi_list = POI.objects.filter(city=city)
    final_path = create_path(poi_list, origin, destination, slider_val, preferences)

    poi_test_list = POI.objects.filter(city='Minneapolis')[:8]

    context = { #'category_dict': category_dict,
                'poi_list': final_path,
                'origin': origin,
                'destination': destination,
                'city': city,
                'start_coords': start_coords,
                'end_coords': end_coords}
    return render(request, 'tour/map.html', context)


