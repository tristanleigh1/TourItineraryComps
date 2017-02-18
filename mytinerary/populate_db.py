import os
import sys
import time
import urllib
import urllib.parse
import urllib.request
from urllib.error import HTTPError
import json
import base64
#from apscheduler.schedulers.blocking import BlockingScheduler

#sched = BlockingScheduler()

def calculate_popularity(business, result_dict):
    popularity = 0
    max_number_of_reviews = business['review_count']
    for b in result_dict['businesses']:
        if b['rating'] == business['rating'] and b['review_count'] > max_number_of_reviews and b['categories'] == business['categories']:
            max_number_of_reviews = b['review_count']

    popularity = (business['rating'] - 1) * 20 + (business['review_count']/float(max_number_of_reviews)) * 20
    return popularity

def adjust_lat_lon(lat, lon):
    radius_lat = (40000 / 1000) * 0.009043
    radius_lon = 0.004
    lat = float(lat)
    lon = float(lon)
    return [(radius_lat + lat, radius_lon + lon), (radius_lat - lat, radius_lon - lon), (radius_lat + lat, radius_lon - lon), (radius_lat - lat, radius_lon + lon)]

#@sched.scheduled_job('cron', day_of_week='sun', hour=3)
def populate_db():
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
    list_of_city_names = ['San Francisco', 'Minneapolis', 'New York', 'London', 'Madrid']

    for i in range(5):
        adj_lat_lon_array = adjust_lat_lon(list_of_cities[i][0], list_of_cities[i][1])
        list_of_cities = list_of_cities + adj_lat_lon_array
        list_of_city_names = list_of_city_names + [list_of_city_names[i], list_of_city_names[i], list_of_city_names[i], list_of_city_names[i]]

    result_dict = {}

    print("Finding POIs...")
    for i, coordinates in enumerate(list_of_cities):
        try:
            query_url1 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s&radius=%s' % (coordinates[0], coordinates[1], 'restaurants', '50', 'rating', '40000')
            request1 = urllib.request.Request(query_url1, None, {"Authorization": "Bearer %s" %access_token})
            response1 = urllib.request.urlopen(request1).read().decode('utf-8')
            data1 = json.loads(response1)
            for j in range(0,len(data1['businesses'])):
                data1['businesses'][j]['category'] = "Restaurants"
                data1['businesses'][j]['location']['city'] = list_of_city_names[i]
                result_dict.setdefault('businesses',[]).append(data1['businesses'][j])
        except:
            continue

        try:
            query_url2 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s&radius=%s' % (coordinates[0], coordinates[1], 'beaches,lakes,parks', '50', 'rating', '40000')
            request2 = urllib.request.Request(query_url2, None, {"Authorization": "Bearer %s" %access_token})
            response2 = urllib.request.urlopen(request2).read().decode('utf-8')
            data2 = json.loads(response2)
            for j in range(0,len(data2['businesses'])):
                data2['businesses'][j]['category'] = "Nature"
                data2['businesses'][j]['location']['city'] = list_of_city_names[i]
                result_dict.setdefault('businesses',[]).append(data2['businesses'][j])
        except:
            continue

        try:
            query_url3 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s&radius=%s' % (coordinates[0], coordinates[1], 'aquariums,zoos,stadiumsarenas', '50', 'rating', '40000')
            request3 = urllib.request.Request(query_url3, None, {"Authorization": "Bearer %s" %access_token})
            response3 = urllib.request.urlopen(request3).read().decode('utf-8')
            data3 = json.loads(response3)
            for j in range(0,len(data3['businesses'])):
                data3['businesses'][j]['category'] = "Activities"
                data3['businesses'][j]['location']['city'] = list_of_city_names[i]
                result_dict.setdefault('businesses',[]).append(data3['businesses'][j])
        except:
            continue

        try:
            query_url4 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s&radius=%s' % (coordinates[0], coordinates[1], 'museums', '25', 'rating', '40000')
            request4 = urllib.request.Request(query_url4, None, {"Authorization": "Bearer %s" %access_token})
            response4 = urllib.request.urlopen(request4).read().decode('utf-8')
            data4 = json.loads(response4)
            for j in range(0,len(data4['businesses'])):
                data4['businesses'][j]['category'] = "Museums"
                data4['businesses'][j]['location']['city'] = list_of_city_names[i]
                result_dict.setdefault('businesses',[]).append(data4['businesses'][j])
        except:
            continue

        try:
            query_url5 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s&radius=%s' % (coordinates[0], coordinates[1], 'landmarks', '25', 'rating', '40000')
            request5 = urllib.request.Request(query_url5, None, {"Authorization": "Bearer %s" %access_token})
            response5 = urllib.request.urlopen(request5).read().decode('utf-8')
            data5 = json.loads(response5)
            for j in range(0,len(data5['businesses'])):
                data5['businesses'][j]['category'] = "Landmarks"
                data5['businesses'][j]['location']['city'] = list_of_city_names[i]
                result_dict.setdefault('businesses',[]).append(data5['businesses'][j])
        except:
            continue

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mytinerary.settings")
    os.environ["DJANGO_SETTINGS_MODULE"] = "mytinerary.settings"
    import django
    django.setup()
    from tour.models import POI

    print("Storing data...")
    for b in result_dict['businesses']:
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
            continue

        if not lon:
            continue
        
        dup_lat_lon_pois = POI.objects.filter(latitude = lat, longitude = lon).exclude(business_name = b.get('name', 'N/A'))
        if dup_lat_lon_pois.exists():
            continue

        b['popularity'] = calculate_popularity(b, result_dict)

        wiki_summary = ""
        if b['category'] != "Restaurants":
            wiki_coordinates ='https://en.wikipedia.org/w/api.php?format=json&action=query&list=geosearch&gsradius=10000&gscoord=%s|%s&gslimit=250' % (lat, lon)
            wiki_coord_request = urllib.request.Request(wiki_coordinates, None, {})
            try:
                wiki_coord_response = urllib.request.urlopen(wiki_coord_request).read().decode('utf-8')
                wiki_coord_dict = json.loads(wiki_coord_response)
            except:
                continue

            for item in wiki_coord_dict['query']['geosearch']:
                if b['name'] == item['title']:
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
        if wiki_summary == "":
            list_of_cats = []
            for category in b['categories']:
                list_of_cats.append(category['title'])
            wiki_summary = ', '.join(list_of_cats)

        p = POI.objects.filter(business_name = b.get('name', 'N/A'), city = b['location']['city'])
        if p:
            p.update(business_name = b['name'],
                        latitude = lat,
                        longitude = lon,
                        address = address_string,
                        city = b['location']['city'],
                        num_stars = b.get('rating',0),
                        num_reviews = b.get('review_count',0),
                        phone_number = b.get('phone','N/A'),
                        price = b.get('price','N/A'),
                        picture_url = b.get('image_url','N/A'),
                        category = b.get('category', 'None'),
                        popularity = b.get('popularity', 0.0),
                        summary = wiki_summary[:3000])
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
                    category = b.get('category', 'None'),
                    popularity = b.get('popularity', 0.0),
                    summary = wiki_summary[:3000])

            p.save()

    print("Complete!")

#sched.start()
#sched.print_jobs()

#while True:
#    time.sleep(10)

#sched.shutdown()

def main():
    populate_db()

if __name__ == "__main__":
    main()
