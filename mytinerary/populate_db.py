import os
import sys
import urllib
import urllib.parse
import urllib.request
from urllib.error import HTTPError
import json
import base64

def calculate_popularity(business, result_dict):
    popularity = 0
    max_number_of_reviews = business['review_count']
    for b in result_dict['businesses']:
        if b['rating'] == business['rating'] and b['review_count'] > max_number_of_reviews and b['categories'] == business['categories']:
            max_number_of_reviews = b['review_count']
    
    popularity = (business['rating'] - 1) * 20 + (business['review_count']/float(max_number_of_reviews)) * 20
    return popularity

client_id = 'utuJWCc9bdvLlOHfbkXThA'
secret = '812V05KxL5KMsYgPTksEl6ZzqILBf9Nv5spXvmtU3M9FAgpxQEYHPLW0QnDP24J8' 

print("Connecting...")
url = 'https://api.yelp.com/oauth2/token'
post_fields = {'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': secret}

encoded_args = urllib.parse.urlencode(post_fields).encode('utf-8')
result = urllib.request.urlopen(url, encoded_args).read().decode()
data = json.loads(result)
access_token = data['access_token']
print("Loading data...")

list_of_cities = [('37.774929', '-122.419416'), ('44.977753', '-93.265011'), ('40.712784', '-74.005941'), ('51.507351', '-0.127758'), ('40.416775', '-3.703790')]

result_dict = {}

for i, coordinates in enumerate(list_of_cities):
    print("Finding restaurants...")
    try:
        query_url1 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s' % (coordinates[0], coordinates[1], 'restaurants', '50', 'rating')
        request1 = urllib.request.Request(query_url1, None, {"Authorization": "Bearer %s" %access_token})
        response1 = urllib.request.urlopen(request1).read().decode('utf-8')
        data1 = json.loads(response1)
        data1['businesses']['categories'] = 'Restaurants'
        result_dict.setdefault('businesses',[]).append(data1['businesses'])
    except:
        continue

    print("Finding Nature...")
    try:
        query_url2 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s' % (coordinates[0], coordinates[1], 'beaches,lakes,parks', '50', 'rating')
        request2 = urllib.request.Request(query_url2, None, {"Authorization": "Bearer %s" %access_token})
        response2 = urllib.request.urlopen(request2).read().decode('utf-8')
        data2 = json.loads(response2)
        data2['businesses']['categories'] = 'Nature'
        result_dict.setdefault('businesses',[]).append(data2['businesses'])
    except:
        continue

    print("Finding Activities...")
    try:
        query_url3 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s' % (coordinates[0], coordinates[1], 'aquariums,zoos,stadiumsarenas', '50', 'rating')
        request3 = urllib.request.Request(query_url3, None, {"Authorization": "Bearer %s" %access_token})
        response3 = urllib.request.urlopen(request3).read().decode('utf-8')
        data3 = json.loads(response3)
        data3['businesses']['categories'] = 'Activities'
        result_dict.setdefault('businesses',[]).append(data3['businesses'])
    except:
        continue

    print("Finding Museums...")
    try:
        query_url4 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s' % (coordinates[0], coordinates[1], 'museums', '25', 'rating')
        request4 = urllib.request.Request(query_url4, None, {"Authorization": "Bearer %s" %access_token})
        response4 = urllib.request.urlopen(request4).read().decode('utf-8')
        data4 = json.loads(response4)
        data4['businesses']['categories'] = 'Museums'
        result_dict.setdefault('businesses',[]).append(data4['businesses'])
    except:
        continue

    print("Finding Landmarks...")
    try:
        query_url5 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s' % (coordinates[0], coordinates[1], 'landmarks', '25', 'rating')
        request5 = urllib.request.Request(query_url5, None, {"Authorization": "Bearer %s" %access_token})
        response5 = urllib.request.urlopen(request5).read().decode('utf-8')
        data5 = json.loads(response5)
        data5['businesses']['categories'] = 'Landmarks'
        result_dict.setdefault('businesses',[]).append(data5['businesses'])
    except:
        continue

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mytinerary.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "mytinerary.settings"
import django
django.setup()
from tour.models import POI

print("Storing data...")
for b in result_dict['businesses']:
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

        b['popularity'] = calculate_popularity(b, result_dict)

        wiki_summary = ""
            
        if b['categories'] == 'Nature' or b['categories'] == 'Museums' or b['categories'] == 'Landmarks' or b['categories'] == 'Activities':
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
                        category = b.get('categories', 'None'),
                        popularity = b.get('popularity', 0.0),
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
                    category = b.get('categories', 'None'),
                    popularity = b.get('popularity', 0.0),
                    summary = wiki_summary)

            p.save()

print("Complete!")
