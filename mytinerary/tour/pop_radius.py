import math
from decimal import *
from .models import *
from django.http import HttpResponse, JsonResponse
import json


'''
    Given distance in kilometers and a latitude, returns the latitude and longitude
    that is that many kilometers away
'''
def km_to_lat_lng(km, latitude):
    # 1km = 0.009043 degrees (for latitude)
    KM_TO_DEGREES_LAT = 0.009043
    # 1km = 0.008983 / cos(latitude) (for longitude)
    degrees_lat = km * KM_TO_DEGREES_LAT
    degrees_lng = km / (111.320 * math.cos(math.radians(latitude)))
    return degrees_lat, degrees_lng

'''
    Function takes in latitude, longitude, radius size, and filter status (binary value representing
    list of categories to show) in JSON object request. Makes call to database. Returns JSON object list of nearby POIs that
    are within the radius and match the filters.
'''
def pop_radius(request):
    if request.method == 'GET':
        latitude = float(request.GET.get('lat', None))
        longitude = float(request.GET.get('lng', None))
        radius_size = float(request.GET.get('radius', None)) / 1000
        filter_status = int(request.GET.get('filter-status', None))

        # Determines which categories to show in radius.
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

        degrees_lat, degrees_lng = km_to_lat_lng(radius_size, latitude)

        nearby_POI_querySets = []
        for i in range(len(categories)):
            # Finds POIs of specified category within radius
            nearby_pois_for_category = POI.objects.filter(category=categories[i], latitude__lte=latitude+degrees_lat, latitude__gte=latitude-degrees_lat, longitude__lte=longitude+degrees_lng, longitude__gte=longitude-degrees_lng)
            nearby_POI_querySets.append(nearby_pois_for_category)
        # Converts django querySets to JSON list of POIs
        response_data = {}
        response_data['nearby_pois'] = list()
        for nearby_pois in nearby_POI_querySets:
            for nearby_poi in nearby_pois:
                response_data['nearby_pois'].append({
                    'name' : nearby_poi.business_name,
                    'latitude' : nearby_poi.latitude,
                    'longitude' : nearby_poi.longitude,
                    'poi_id' : nearby_poi.id,
                    'address' : nearby_poi.address,
                    'rating' : nearby_poi.popularity,
                    'category': nearby_poi.category,
                    'summary': nearby_poi.summary
                })
        return JsonResponse(response_data)
    else:
        return HttpResponse(
                json.dumps({"error":"an error occured."}),
                content_type="application/json"
        )
