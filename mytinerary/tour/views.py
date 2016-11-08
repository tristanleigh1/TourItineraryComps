from django.shortcuts import get_object_or_404, get_list_or_404, render
from .models import *

# Create your views here.
#GET: tour/
def index(request):
    return render(request, 'tour/index.html')

#GET: tour/map/
def map(request):

    poi_list = POI.objects.filter(city='Minneapolis')[:8]
    number = 0
    # category_dict = {}
    # for poi in poi_list:
    #     categories = POI.objects.values_list('category', flat=True).filter(id = poi.id)
    #     category_dict[poi.id] = categories

    origin = get_object_or_404(POI, pk=1393)
    destination = get_object_or_404(POI, pk=1392)
    #origin = "a"
    #destination = "b"

    # Caleb's tests
    city = request.GET['city']
    start_choice = request.GET['startDestination']
    end_choice = request.GET['endDestination']
    slider_val = request.GET['points']

    final_path = create_path(poi_list, start_choice, end_choice, slider_val)

    context = { #'category_dict': category_dict,
                'poi_list': poi_list,
                'origin': origin,
                'destination': destination,
                'start_choice': start_choice,
                'end_choice': end_choice,
                'slider_val': slider_val,
                'testing' : test,
                'city': city}
    return render(request, 'tour/map.html', context)


def calculate_score(current_poi, path_segments):
    empirical_coefficient = 0.0002
    category = current_poi.category
    popularity = current_poi.popularity
    walk_factor = request.GET['points'] * (3.0 / 10.0) # Put on a scale of 0-3
    preferred_pois = request.GET['POIChoice']
    distance_to_path = None
    closest_segment = None
    score = float("inf")

    for seg in path_segments:
        slope = (seg[1].latitude - seg[0].latitude) / (seg[1].longitude - seg[0].longitude)
        y_int = (seg[0].latitude - slope * seg[0].longitude)
        orthogonal_slope = slope * -1
        orthogonal_y_int = (current_poi.latitude - slope * current_poi.longitude)

        intersect_x = (y_int - orthogonal_y_int) / (2 * slope)
        intersect_y = (slope * intersect_y) + y_int

        distance_to_segment = ((intersect_x - current_poi.longitude)**2 + (intersect_y - current_poi.latitude)**2)**0.5

        if distance_to_segment < distance_to_path:
            distance_to_path = distance_to_segment
            closest_segment = seg

    return score, closest_segment

def create_path(total_pois, start, end):
    MAX_POIS = 8
    # path_segments is a list of pairs of points
    path_segments = [(start, end)]
    path_pois = []

    while len(path_pois) < MAX_POIS:
        poi = find_next_poi(total_pois, path_segments)
        path_pois.append(poi)
        # Not sure if remove is correct
        total_pois.remove(poi)

    return path_pois

def update_segments(current_segments, new_poi, segment_to_add_to):
    new_segment = (current_segments[segment_to_add_to][0], new_poi)
    current_segments[segment_to_add_to] = (new_poi, current_segments[segment_to_add_to][1])
    current_segments.insert(segment_to_add_to, new_segment)

def find_next_poi(poi_list, path_segments):
    poi_to_add = None
    segment = None
    min_score = float("inf")
    for poi in poi_list:
        score, segment = calculate_score(poi, path_segments)
        if score < min_score:
            poi_to_add = poi
            min_score = score

    update_segments(path_segments, poi_to_add, segment)

    return poi_to_add
