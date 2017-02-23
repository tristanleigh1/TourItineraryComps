import os
import sys
import time
import urllib
import urllib.parse
import urllib.request
from urllib.error import HTTPError
import json
import base64
from decimal import *

'''
    Calculates popularity score of given business based on equation described in project paper
'''
def calculate_popularity(business, result_dict):
    popularity = 0
    max_number_of_reviews = business['review_count']
    for b in result_dict['businesses']:
        # If the current iteration's business has the same category/rating as the given business, and has more
        # reviews than the current max number of reviews, update the max number of reviews for that category/rating
        if b['rating'] == business['rating'] and b['review_count'] > max_number_of_reviews and b['categories'] == business['categories']:
            max_number_of_reviews = b['review_count']

    popularity = (business['rating'] - 1) * 20 + (business['review_count']/float(max_number_of_reviews)) * 20
    return popularity

'''
    Creates 4 more latitude/longitude pairs for a given latitude and longitude. These 4 new pairs will be on each "corner"
    of the given latitude and longitude's radius.
'''
def adjust_lat_lon(lat, lon):
    radius_lat = (40000 / 1000) * 0.009043
    radius_lon = 0.004
    lat = float(lat)
    lon = float(lon)
    return [(radius_lat + lat, radius_lon + lon), (radius_lat - lat, radius_lon - lon), (radius_lat + lat, radius_lon - lon), (radius_lat - lat, radius_lon + lon)]

'''
    Function that populates/updates our DB.
'''
def populate_db():
    client_id = 'utuJWCc9bdvLlOHfbkXThA'
    secret = '812V05KxL5KMsYgPTksEl6ZzqILBf9Nv5spXvmtU3M9FAgpxQEYHPLW0QnDP24J8'
    google_key = 'AIzaSyBm67Q0-cr3JdKnXVOmwqfQkrTIzmsDfi4'
    cx = '000383868601621521479:vfsikrtcoe8'

    print("Connecting...")
    url = 'https://api.yelp.com/oauth2/token'
    post_fields = {'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': secret}

    # Get access token
    encoded_args = urllib.parse.urlencode(post_fields).encode('utf-8')
    result = urllib.request.urlopen(url, encoded_args).read().decode()
    data = json.loads(result)
    access_token = data['access_token']
    print("Loading data...")

    list_of_cities = [('37.774929', '-122.419416'), ('44.977753', '-93.265011'), ('40.712784', '-74.005941'), ('51.507351', '-0.127758'), ('40.416775', '-3.703790')]
    list_of_city_names = ['San Francisco', 'Minneapolis', 'New York', 'London', 'Madrid']

    # Create 4 additional lat/lon pairs for each lat/lon in our list of cities, and adjust the list of city names
    # accordingly to match each lat/lon pair.
    for i in range(5):
        adj_lat_lon_array = adjust_lat_lon(list_of_cities[i][0], list_of_cities[i][1])
        list_of_cities = list_of_cities + adj_lat_lon_array
        list_of_city_names = list_of_city_names + [list_of_city_names[i], list_of_city_names[i], list_of_city_names[i], list_of_city_names[i]]

    result_dict = {}

    print("Finding POIs...")
    # Iterate through each city coordinate pair and for each of these coordinates, query yelp for the
    # given categories and store the results in the dictionary after replacing each business's category
    # with one of our 5 categories.
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
            raise Exception("4")
            continue
        try:
            query_url2 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s&radius=%s' % (coordinates[0], coordinates[1], 'cafes,bagels,bubbletea,coffee,bakeries,gelato', '20', 'rating', '40000')
            request2 = urllib.request.Request(query_url2, None, {"Authorization": "Bearer %s" %access_token})
            response2 = urllib.request.urlopen(request2).read().decode('utf-8')
            data2 = json.loads(response2)
            for j in range(0,len(data2['businesses'])):
                data2['businesses'][j]['category'] = "Restaurants"
                data2['businesses'][j]['location']['city'] = list_of_city_names[i]
                result_dict.setdefault('businesses',[]).append(data2['businesses'][j])
        except:
            raise Exception("5")
            continue
        try:
            query_url3 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s&radius=%s' % (coordinates[0], coordinates[1], 'asianfusion,bbq,basque,breakfast_brunch,buffets,caribbean,chinese', '20', 'rating', '40000')
            request3 = urllib.request.Request(query_url3, None, {"Authorization": "Bearer %s" %access_token})
            response3 = urllib.request.urlopen(request3).read().decode('utf-8')
            data3 = json.loads(response3)
            for j in range(0,len(data3['businesses'])):
                data3['businesses'][j]['category'] = "Restaurants"
                data3['businesses'][j]['location']['city'] = list_of_city_names[i]
                result_dict.setdefault('businesses',[]).append(data3['businesses'][j])
        except:
            raise Exception("6")
            continue
        try:
            query_url4 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s&radius=%s' % (coordinates[0], coordinates[1], 'comfortfood,creperies,cuban,diners,delis,dinnertheater,hotdogs,fishnchips,fondue,italian,foodstands,french', '40', 'rating', '40000')
            request4 = urllib.request.Request(query_url4, None, {"Authorization": "Bearer %s" %access_token})
            response4 = urllib.request.urlopen(request4).read().decode('utf-8')
            data4 = json.loads(response4)
            for j in range(0,len(data4['businesses'])):
                data4['businesses'][j]['category'] = "Restaurants"
                data4['businesses'][j]['location']['city'] = list_of_city_names[i]
                result_dict.setdefault('businesses',[]).append(data4['businesses'][j])
        except:
            raise Exception("7")
            continue
        try:
            query_url5 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s&radius=%s' % (coordinates[0], coordinates[1], 'japanese,kebab,kosher,latin,mediterranean,mexican,mideastern,pizza,salad,sandwiches', '20', 'rating', '40000')
            request5 = urllib.request.Request(query_url5, None, {"Authorization": "Bearer %s" %access_token})
            response5 = urllib.request.urlopen(request5).read().decode('utf-8')
            data5 = json.loads(response5)
            for j in range(0,len(data5['businesses'])):
                data5['businesses'][j]['category'] = "Restaurants"
                data5['businesses'][j]['location']['city'] = list_of_city_names[i]
                result_dict.setdefault('businesses',[]).append(data5['businesses'][j])
        except:
            raise Exception("8")
            continue
        try:
            query_url6 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s&radius=%s' % (coordinates[0], coordinates[1], 'portuguese,seafood,soup,steak,spanish,vegetarian', '20', 'rating', '40000')
            request6 = urllib.request.Request(query_url6, None, {"Authorization": "Bearer %s" %access_token})
            response6 = urllib.request.urlopen(request6).read().decode('utf-8')
            data6 = json.loads(response6)
            for j in range(0,len(data6['businesses'])):
                data6['businesses'][j]['category'] = "Restaurants"
                data6['businesses'][j]['location']['city'] = list_of_city_names[i]
                result_dict.setdefault('businesses',[]).append(data6['businesses'][j])
        except:
            raise Exception("9")
            continue
        try:
            query_url7 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s&radius=%s' % (coordinates[0], coordinates[1], 'tapas,vegan,tapasmallplates', '20', 'rating', '40000')
            request7 = urllib.request.Request(query_url7, None, {"Authorization": "Bearer %s" %access_token})
            response7 = urllib.request.urlopen(request7).read().decode('utf-8')
            data7 = json.loads(response7)
            for j in range(0,len(data7['businesses'])):
                data7['businesses'][j]['category'] = "Restaurants"
                data7['businesses'][j]['location']['city'] = list_of_city_names[i]
                result_dict.setdefault('businesses',[]).append(data7['businesses'][j])
        except:
            raise Exception("10")
            continue
        try:
            query_url8 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s&radius=%s' % (coordinates[0], coordinates[1], 'bars', '50', 'rating', '40000')
            request8 = urllib.request.Request(query_url8, None, {"Authorization": "Bearer %s" %access_token})
            response8 = urllib.request.urlopen(request8).read().decode('utf-8')
            data8 = json.loads(response8)
            for j in range(0,len(data8['businesses'])):
                data8['businesses'][j]['category'] = "Restaurants"
                data8['businesses'][j]['location']['city'] = list_of_city_names[i]
                result_dict.setdefault('businesses',[]).append(data8['businesses'][j])
        except:
            raise Exception("11")
            continue

        try:
            query_url9 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s&radius=%s' % (coordinates[0], coordinates[1], 'parks,playgrounds', '25', 'rating', '40000')
            request9 = urllib.request.Request(query_url9, None, {"Authorization": "Bearer %s" %access_token})
            response9 = urllib.request.urlopen(request9).read().decode('utf-8')
            data9 = json.loads(response9)
            for j in range(0,len(data9['businesses'])):
                data9['businesses'][j]['category'] = "Nature"
                data9['businesses'][j]['location']['city'] = list_of_city_names[i]
                result_dict.setdefault('businesses',[]).append(data9['businesses'][j])
        except:
            raise Exception("12")
            continue
        try:
            query_url10 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s&radius=%s' % (coordinates[0], coordinates[1], 'beaches,hiking', '50', 'rating', '40000')
            request10 = urllib.request.Request(query_url10, None, {"Authorization": "Bearer %s" %access_token})
            response10 = urllib.request.urlopen(request10).read().decode('utf-8')
            data10 = json.loads(response10)
            for j in range(0,len(data10['businesses'])):
                data10['businesses'][j]['category'] = "Nature"
                data10['businesses'][j]['location']['city'] = list_of_city_names[i]
                result_dict.setdefault('businesses',[]).append(data10['businesses'][j])
        except:
            raise Exception("13")
            continue
        try:
            query_url11 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s&radius=%s' % (coordinates[0], coordinates[1], 'lakes,farms', '50', 'rating', '40000')
            request11 = urllib.request.Request(query_url11, None, {"Authorization": "Bearer %s" %access_token})
            response11 = urllib.request.urlopen(request11).read().decode('utf-8')
            data11 = json.loads(response11)
            for j in range(0,len(data11['businesses'])):
                data11['businesses'][j]['category'] = "Nature"
                data11['businesses'][j]['location']['city'] = list_of_city_names[i]
                result_dict.setdefault('businesses',[]).append(data11['businesses'][j])
        except:
            raise Exception("14")
            continue
        try:
            query_url12 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s&radius=%s' % (coordinates[0], coordinates[1], 'parklets,gardens', '50', 'rating', '40000')
            request12 = urllib.request.Request(query_url12, None, {"Authorization": "Bearer %s" %access_token})
            response12 = urllib.request.urlopen(request12).read().decode('utf-8')
            data12 = json.loads(response12)
            for j in range(0,len(data12['businesses'])):
                data12['businesses'][j]['category'] = "Nature"
                data12['businesses'][j]['location']['city'] = list_of_city_names[i]
                result_dict.setdefault('businesses',[]).append(data12['businesses'][j])
        except:
            raise Exception("15")
            continue
        try:
            query_url13 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s&radius=%s' % (coordinates[0], coordinates[1], 'amusementparks,aquariums,bowling,bungeejumping,challengecourses,escapegames,gokarts,lasertag,parasailing,paintball,waterparks,zoos', '50', 'rating', '40000')
            request13 = urllib.request.Request(query_url13, None, {"Authorization": "Bearer %s" %access_token})
            response13 = urllib.request.urlopen(request13).read().decode('utf-8')
            data13 = json.loads(response13)
            for j in range(0,len(data13['businesses'])):
                data13['businesses'][j]['category'] = "Activities"
                data13['businesses'][j]['location']['city'] = list_of_city_names[i]
                result_dict.setdefault('businesses',[]).append(data13['businesses'][j])
        except:
            raise Exception("1")
            continue
        try:
            query_url14 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s&radius=%s' % (coordinates[0], coordinates[1], 'casinos,movietheaters,festivals,musicvenues,observatories,racetracks,stadiumsarenas,rodeo,wineries,tastingclasses,arcades,festivals,tablaoflamenco,breweries', '50', 'rating', '40000')
            request14 = urllib.request.Request(query_url14, None, {"Authorization": "Bearer %s" %access_token})
            response14 = urllib.request.urlopen(request14).read().decode('utf-8')
            data14 = json.loads(response14)
            for j in range(0,len(data14['businesses'])):
                data14['businesses'][j]['category'] = "Activities"
                data14['businesses'][j]['location']['city'] = list_of_city_names[i]
                result_dict.setdefault('businesses',[]).append(data14['businesses'][j])
        except:
            raise Exception("2")
            continue
        try:
            query_url16 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s&radius=%s' % (coordinates[0], coordinates[1], 'beergarden,comedyclubs,danceclubs,karaoke', '25', 'rating', '40000')
            request16 = urllib.request.Request(query_url16, None, {"Authorization": "Bearer %s" %access_token})
            response16 = urllib.request.urlopen(request16).read().decode('utf-8')
            data16 = json.loads(response16)
            for j in range(0,len(data16['businesses'])):
                data16['businesses'][j]['category'] = "Activities"
                data16['businesses'][j]['location']['city'] = list_of_city_names[i]
                result_dict.setdefault('businesses',[]).append(data16['businesses'][j])
        except:
            raise Exception("3")
            continue
        try:
            query_url17 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s&radius=%s' % (coordinates[0], coordinates[1], 'artmuseums', '50', 'rating', '40000')
            request17 = urllib.request.Request(query_url17, None, {"Authorization": "Bearer %s" %access_token})
            response17 = urllib.request.urlopen(request17).read().decode('utf-8')
            data17 = json.loads(response17)
            for j in range(0,len(data17['businesses'])):
                data17['businesses'][j]['category'] = "Museums"
                data17['businesses'][j]['location']['city'] = list_of_city_names[i]
                result_dict.setdefault('businesses',[]).append(data17['businesses'][j])
        except:
            continue
        try:
            query_url18 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s&radius=%s' % (coordinates[0], coordinates[1], 'museums', '50', 'rating', '40000')
            request18 = urllib.request.Request(query_url18, None, {"Authorization": "Bearer %s" %access_token})
            response18 = urllib.request.urlopen(request18).read().decode('utf-8')
            data18 = json.loads(response18)
            for j in range(0,len(data18['businesses'])):
                data18['businesses'][j]['category'] = "Museums"
                data18['businesses'][j]['location']['city'] = list_of_city_names[i]
                result_dict.setdefault('businesses',[]).append(data18['businesses'][j])
        except:
            continue

        try:
            query_url19 = 'https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&categories=%s&limit=%s&sort_by=%s&radius=%s' % (coordinates[0], coordinates[1], 'landmarks', '50', 'rating', '40000')
            request19 = urllib.request.Request(query_url19, None, {"Authorization": "Bearer %s" %access_token})
            response19 = urllib.request.urlopen(request19).read().decode('utf-8')
            data19 = json.loads(response19)
            for j in range(0,len(data19['businesses'])):
                data19['businesses'][j]['category'] = "Landmarks"
                data19['businesses'][j]['location']['city'] = list_of_city_names[i]
                result_dict.setdefault('businesses',[]).append(data19['businesses'][j])
        except:
            continue


    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mytinerary.settings")
    os.environ["DJANGO_SETTINGS_MODULE"] = "mytinerary.settings"
    import django
    django.setup()
    from tour.models import POI

    print("Storing data...")
    for b in result_dict['businesses']:
        # If the business doesn't have a latitude or longitude, continue to the next business
        if not b['coordinates']['latitude']:
            continue

        if not b['coordinates']['longitude']:
            continue

        # Lat/lons in DB are length 17 in decimal place, must convert Yelp lat/lon to match.
        # Python does some weird rounding when trying add zeros to the end of decimals,
        # hence the ugly code below.
        str_lat = str(b['coordinates']['latitude'])
        str_lon = str(b['coordinates']['longitude'])
        num_lat, dec_lat = str_lat.split('.')
        num_lon, dec_lon = str_lon.split('.')
        if len(dec_lat) < 17:
            zeros = ""
            num_zeros_added = 17-len(dec_lat)
            for i in range(0, num_zeros_added):
            	zeros += "0"
            str_lat += zeros
        if len(dec_lon) < 17:
            zeros = ""
            num_zeros_added = 17-len(dec_lon)
            for i in range(0, num_zeros_added):
            	zeros += "0"
            str_lon += zeros

        lat = Decimal(str_lat)
        lon = Decimal(str_lon)

        # If a business in our DB with the same latitude/longitude but a different business name
        # as the current business of the iteration exists, then continue to the next business
        dup_lat_lon_pois = POI.objects.filter(latitude = lat, longitude = lon).exclude(business_name = b['name'])
        if dup_lat_lon_pois.exists():
            continue

        # Format address
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

        b['popularity'] = calculate_popularity(b, result_dict)

        # If the business is not a restaurant, check wikipedia for a summary for the business.
        # First, we google search for the wikipedia page of our business, and if no page matches
        # our business's name, then look for wikipedia pages that match our business's coordinates.
        wiki_summary = ""
        wiki_business_name = ""
        if b['category'] != "Restaurants":
            google_search = 'https://www.googleapis.com/customsearch/v1?key=%s&cx=%s&q=%s' % (google_key, cx, b['name'].replace(" ", "+"))
            google_request = urllib.request.Request(google_search, None, {})
            try:
                google_response = urllib.request.urlopen(google_request).read().decode('utf-8')
                google_dict = json.loads(google_response)
                if google_dict['items'][0]['title'].endswith(' - Wikipedia'):
                    wiki_business_name = google_dict['items'][0]['title'][:-12]
                    if wiki_business_name not in b['name']:
                        wiki_business_name = ""
            except:
                pass

            if wiki_business_name == "":
                wiki_coordinates ='https://en.wikipedia.org/w/api.php?format=json&action=query&list=geosearch&gsradius=10000&gscoord=%s|%s&gslimit=250' % (lat, lon)
                wiki_coord_request = urllib.request.Request(wiki_coordinates, None, {})
                try:
                    wiki_coord_response = urllib.request.urlopen(wiki_coord_request).read().decode('utf-8')
                    wiki_coord_dict = json.loads(wiki_coord_response)
                except:
                    pass

                for item in wiki_coord_dict['query']['geosearch']:
                    if b['name'] == item['title']:
                        wiki_url = 'https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles=%s' % (b['name'].replace(" ", "%20"))
                        wiki_request = urllib.request.Request(wiki_url, None, {})
                        try:
                            wiki_response = urllib.request.urlopen(wiki_request).read().decode('utf-8')
                            wiki_dict = json.loads(wiki_response)
                        except:
                            pass

                        page_id = list(wiki_dict['query']['pages'].keys())[0]
                        if page_id != '-1':
                            wiki_summary = wiki_dict['query']['pages'][page_id]['extract']
            else:
                wiki_url = 'https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles=%s' % (wiki_business_name.replace(" ", "%20"))
                wiki_request = urllib.request.Request(wiki_url, None, {})
                try:
                    wiki_response = urllib.request.urlopen(wiki_request).read().decode('utf-8')
                    wiki_dict = json.loads(wiki_response)
                except:
                    pass

                page_id = list(wiki_dict['query']['pages'].keys())[0]
                if page_id != '-1':
                    wiki_summary = wiki_dict['query']['pages'][page_id]['extract']

        # If no wikipedia summary has been found, just use the Yelp categories
        if wiki_summary == "":
            list_of_cats = []
            for category in b['categories']:
                list_of_cats.append(category['title'])
            wiki_summary = ', '.join(list_of_cats)

        # Find business with the same latitude, longitude, and name. If such a business
        # exists, just update the business rather than create a duplicate entry
        p = POI.objects.filter(latitude = lat, longitude = lon, business_name = b['name'])
        p2 = POI.objects.filter(business_name = b['name'], city = b['location']['city'])
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
        elif p2:
            p2.update(business_name = b['name'],
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

def main():
    populate_db()

if __name__ == "__main__":
    main()
