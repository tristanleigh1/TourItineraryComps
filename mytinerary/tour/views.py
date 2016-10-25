from django.shortcuts import render

# Create your views here.
#GET: tour/
def index(request):
    return render(request, 'tour/index.html')

#POST: tour/map/
def map(request):
    return render(request, 'tour/map.html')
