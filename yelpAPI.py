# A script to get ratings of places on Yelp

import urllib
import urllib2
import json
import base64
import time

def calculate_popularity(business, result_dict):
	popularity = 0
	max_number_of_reviews = 0
	for i in result_dict['businesses']:
		if i['rating'] == business['rating'] and i['review_count'] > max_number_of_reviews:
			max_number_of_reviews = i['review_count']
	
	popularity = (business['rating'] - 1) * 20 + (business['review_count']/float(max_number_of_reviews)) * 20
	return popularity

start = time.time()

client_id = 'utuJWCc9bdvLlOHfbkXThA'
secret = '812V05KxL5KMsYgPTksEl6ZzqILBf9Nv5spXvmtU3M9FAgpxQEYHPLW0QnDP24J8' 

url = 'https://api.yelp.com/oauth2/token' # Set destination URL here
post_fields = {'grant_type': 'client_credentials',
		'client_id': client_id,
		'client_secret': secret}     # Set POST fields here

print 'Retrieving access token'
encoded_args = urllib.urlencode(post_fields)
result = urllib2.urlopen(url, encoded_args).read().decode()
result = json.loads(result)
access_token = result['access_token']

lat = '37.786882'
lon = '-122.399972'

print 'Finding restaurants that deliver near latitude ' + lat + ' and longitude ' + lon
query_url = 'https://api.yelp.com/v3/transactions/delivery/search?latitude=%s&longitude=%s' % (lat, lon)
request = urllib2.Request(query_url, None, {"Authorization": "Bearer %s" %access_token})
response = urllib2.urlopen(request)

html = response.read()
result_dict = json.loads(html)

print 'Printing restaurants with a rating of 3 or more stars'
for b in result_dict['businesses']:
	if b['rating'] >= 3:
		print b['rating'], 'stars\t\t', 'Popularity Score: ' + "{:.3f}".format(calculate_popularity(b, result_dict)) + '/100.\t\t', b['name']
		print

end = time.time()
print 'API call runtime: ' + "{:.5f}".format(end - start) + ' seconds.'


