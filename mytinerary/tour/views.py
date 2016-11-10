from django.shortcuts import get_object_or_404, get_list_or_404, render
from .models import *

# Create your views here.
#GET: tour/
def index(request):
    return render(request, 'tour/index.html')

#GET: tour/map/
def map(request):

    poi_list = POI.objects.filter(city="San Francisco")[:8]
    number = 0
    category_dict = {}
#    for poi in poi_list:
#        categories = POI.objects.values_list('category', flat=True).filter(id = poi.id)
#        category_dict[poi.id] = categories

    origin = get_object_or_404(POI, pk=1231)
    destination = get_object_or_404(POI, pk=1295)

    # Caleb's tests
    city = request.GET['city']
    start_choice = request.GET['startDestination']
    end_choice = request.GET['endDestination']
    slider_val = request.GET['points']
    test = "test"#calculate_score(poi_list[0])

    context = { 'category_dict': category_dict,
                'poi_list': poi_list,
                'origin': origin,
                'destination': destination,
                'start_choice': start_choice,
                'end_choice': end_choice,
                'slider_val': slider_val,
                'testing' : test,
                'city': city}
    return render(request, 'tour/map.html', context)


def calculate_score(poi_obj):
    poi_name = poi_obj
    poi_rating = poi_obj.num_stars
    return "" + poi_name + " has a rating of " + poi_rating
