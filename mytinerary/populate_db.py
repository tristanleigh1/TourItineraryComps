import os
import sys
import urllib
import urllib.parse
import urllib.request
from urllib.error import HTTPError
import json
import base64
import time

client_id = 'utuJWCc9bdvLlOHfbkXThA'
secret = '812V05KxL5KMsYgPTksEl6ZzqILBf9Nv5spXvmtU3M9FAgpxQEYHPLW0QnDP24J8' 

print("Connecting...")
url = 'https://api.yelp.com/oauth2/token' # Set destination URL here
post_fields = {'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': secret}     # Set POST fields here

encoded_args = urllib.parse.urlencode(post_fields).encode('utf-8')
result = urllib.request.urlopen(url, encoded_args).read().decode()
result = json.loads(result)
access_token = result['access_token']
print("Loading data...")

list_of_cities = [('37.774929', '-122.419416'), ('44.977753', '-93.265011'), ('40.712784', '-74.005941'), ('51.507351', '-0.127758'), ('40.416775', '-3.703790')]
#list_of_cities = ['San Francisco', 'Minneapolis', 'New York', 'London', 'Madrid']
result_dict = {}

print("Finding restaurants...")
for i, coordinates in enumerate(list_of_cities):
    query_url = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s' % (coordinates[0], coordinates[1], 'restaurants', '50', 'rating')
    request = urllib.request.Request(query_url, None, {"Authorization": "Bearer %s" %access_token})
    try:
        response = urllib.request.urlopen(request).read().decode('utf-8')
        data = json.loads(response)
        result_dict.setdefault(i,[]).append(data['businesses'])
    except:
        continue

print("Finding POI's...")
for i, coordinates in enumerate(list_of_cities):
    query_url = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s' % (coordinates[0], coordinates[1], 'aquariums,beaches,lakes,parks,zoos,museums,stadiumsarenas,landmarks', '50', 'rating')
    request = urllib.request.Request(query_url, None, {"Authorization": "Bearer %s" %access_token})
    try:
        response = urllib.request.urlopen(request).read().decode('utf-8')
        data = json.loads(response)
        result_dict.setdefault(i,[]).append(data['businesses'])
    except:
        continue

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mytinerary.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "mytinerary.settings"
import django
django.setup()
from tour.models import POI, Category_Type, POI_Type

print("Storing data...")
for i in range(0,len(list_of_cities)):
    for set_of_businesses in result_dict[i]:
        for b in set_of_businesses:
            if b['rating'] >= 3:
                address_string = ""
                if b['location']['address1']:
                    address_string += b['location']['address1'] + " "
                if b['location']['address2']:
                    address_string += b['location']['address2'] + " "
                if b['location']['address3']:
                    address_string += b['location']['address3'] + " "
                if b['location']:
                    address_string += b['location']['city'] + ", "
                if b['location']['state']:
                    address_string += b['location']['state'] + " "
                if b['location']['zip_code']:
                    address_string += b['location']['zip_code'] + " "
                if b['location']['country']:
                    address_string += b['location']['country']
            
                lat = b['coordinates']['latitude']
                lon = b['coordinates']['longitude']
                if not lat:
                    lat = list_of_cities[i][0]

                if not lon:
                    lon = list_of_cities[i][1]

                list_of_categories = []
                wiki_summary = ""
                for category in b['categories']:
                    list_of_categories.append(category['alias'])
                    
                if 'aquariums' in list_of_categories or 'beaches' in list_of_categories or 'lakes' in list_of_categories or 'parks' in list_of_categories or 'zoos' in list_of_categories or 'museums' in list_of_categories or 'stadiumsarenas' in list_of_categories or 'landmarks' in list_of_categories:
                    wiki_url = 'https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles=%s' % (b['name'].replace(" ", "%20"))
                    wiki_request = urllib.request.Request(wiki_url, None, {})
                    try:
                        wiki_response = urllib.request.urlopen(wiki_request).read().decode('utf-8')
                        wiki_dict = json.loads(wiki_response)
                    except:
                        continue
                        
                    page_id = list(wiki_dict['query']['pages'].keys())[0]
                    if page_id != '-1':
                        wiki_summary = wiki_dict['query']['pages'][page_id]['extract']
                

                p = POI.objects.filter(business_name = b.get('name', 'N/A'), city = b['location']['city'])
                if p:
                    p.update(business_name = b.get('name','N/A'),
                                latitude = lat,
                                longitude = lon,
                                address = address_string,
                                city = b['location']['city'],
                                num_stars = b.get('rating',0),
                                num_reviews = b.get('review_count',0),
                                phone_number = b.get('phone','N/A'),
                                price = b.get('price','N/A'),
                                picture_url = b.get('image_url','N/A'),
                                summary = wiki_summary)
                else:
                    p = POI(business_name = b.get('name','N/A'),
                            latitude = lat,
                            longitude = lon,
                            address = address_string,
                            city = b['location']['city'],
                            num_stars = b.get('rating',0),
                            num_reviews = b.get('review_count',0),
                            phone_number = b.get('phone','N/A'),
                            price = b.get('price','N/A'),
                            picture_url = b.get('image_url','N/A'),
                            summary = wiki_summary)

                    p.save()
            
                # not 100% sure this works either
                for category in b['categories']:
                    obj, created = Category_Type.objects.get_or_create(category_name = category['title'])
                    if created:
                        poi_cat = POI_Type(category_name = obj, poi_id = p)
                        poi_cat.save()

print("Complete!")
