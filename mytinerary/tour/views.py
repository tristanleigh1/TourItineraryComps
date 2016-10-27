from django.shortcuts import get_object_or_404, render

from .models import *
# Create your views here.
#GET: tour/
def index(request):
    return render(request, 'tour/index.html')

#GET: tour/map/
def map(request):
#    poi = get_object_or_404(POI, pk=1)
    poi_list = POI.objects.all()
    context = {'poi_list': poi_list}
    return render(request, 'tour/map.html', context)
