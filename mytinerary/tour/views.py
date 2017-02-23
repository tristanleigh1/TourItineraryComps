from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from .models import *
from decimal import *
from .calculate_route import *
from .pop_radius import *
from .send_directions import *


''' Renders the home page. '''
def index(request):
    return render(request, 'tour/index.html')

''' Renders the about page. '''
def about(request):
    return render(request, 'tour/about.html')

''' Renders the contact us page. '''
def contact(request):
    return render(request, 'tour/contact.html')

''' Renders the map page. '''
def map(request):
    mode = request.GET['mode']
    if (mode == "start-to-end"):
        return startToEnd(request)
    elif (mode == "exploratory"):
        return exploratory(request)

'''
    Given a start point and city in a JSON request object, plots the origin point on the map
    page.
'''
def exploratory(request):
    city = request.GET['city']
    start_coords = request.GET['startCoords']

    origin = POI()
    origin.latitude = Decimal(start_coords[1:-1].split(", ")[0])
    origin.longitude = Decimal(start_coords[1:-1].split(", ")[1])
    origin.business_name = request.GET['startDestination'].split(',')[0]
    origin.category = "Origin"

    context = { 'mode': "exploratory",
                'origin': origin,
                'city': city,
                'start_coords': start_coords}
    return render(request, 'tour/map.html', context)

'''
    Given a city, a start and end point, and user preferences, calculates path for user
    and plots path on map page.
'''
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

    context = { 'mode': 'startToEnd',
                'poi_list': final_path,
                'origin': origin,
                'destination': destination,
                'city': city}
    return render(request, 'tour/map.html', context)
