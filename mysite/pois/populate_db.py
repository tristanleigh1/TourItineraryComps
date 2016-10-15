import os
import sys
import urllib
import urllib2
import json
import base64
import time

client_id = 'utuJWCc9bdvLlOHfbkXThA'
secret = '812V05KxL5KMsYgPTksEl6ZzqILBf9Nv5spXvmtU3M9FAgpxQEYHPLW0QnDP24J8' 

url = 'https://api.yelp.com/oauth2/token' # Set destination URL here
post_fields = {'grant_type': 'client_credentials',
		'client_id': client_id,
		'client_secret': secret}     # Set POST fields here

encoded_args = urllib.urlencode(post_fields)
result = urllib2.urlopen(url, encoded_args).read().decode()
result = json.loads(result)
access_token = result['access_token']

list_of_cities = ["San Francisco", "Minneapolis", "New York", "London", "Madrid"]
result_dict = {}

for city in list_of_cities:
    query_url = 'https://api.yelp.com/v3/businesses/search?location=%s' % (city)
    request = urllib2.Request(query_url, None, {"Authorization": "Bearer %s" %access_token})
    response = urllib2.urlopen(request)

    html = response.read()
    result_dict = result_dict.update(json.loads(html))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "mysite.settings"
import django
django.setup()

from pois.models import POI
from pois.models import Category_Type
from pois.models import POI_Type

for b in result_dict['businesses']:
    address_string = ""
    if b['location.address1']:
        address_string += b['location.address1'] + " "
    if b['location.address2']:
        address_string += b['location.address2'] + " "
    if b['location.address3']:
        address_string += b['location.address3'] + " "
    if b['location.city']:
        address_string += b['location.city'] + ", "
    if b['location.state']:
        address_string += b['location.state'] + " "
    if b['location.zip_code']:
        address_string += b['location.zip_code'] + " "
    if b['location.country']:
        address_string += b['location.country']
    
    # not 100% sure this works
    wiki_url = 'https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles=%s' % (b['name'].replace(" ", "%20"))
    wiki_request = urllib2.Request(wiki_url, None, {})
    wiki_response = urllib2.urlopen(wiki_request)
    wiki_html = wiki_response.read()
    wiki_dict = json.loads(wiki_html)
    #
    
    p = POI(business_name = b['name'],
            latitude = b['coordinates.latitude'],
            longitude = b['coordinates.longitude'],
            address = address_string,
            city = b['location.city'],
            num_stars = b['rating'],
            num_reviews = b['review_count'],
            phone_number = b['phone'],
            price = b['price'],
            picture_url = b['image_url'],
            summary = wiki_dict['extract'])
    
    p.save()
    
    # not 100% sure this works either
    for category in b['categories']:
        poi_cat = POI_Type(category_name = category.title,
                 poi_id = p.id)
        
        poi_cat.save()
    #    
    # Still need to figure out a way to get max num of reviews. Necessary?
        #obj, created = Category_Type.objects.get_or_create(category_name = category.title, max_num_reviews = b['num_reviews'])
