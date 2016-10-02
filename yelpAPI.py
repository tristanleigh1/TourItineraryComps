# A script to get ratings of places on Yelp

import urllib
import urllib2
import json
import base64

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

print 'Printing restaurants with a rating of 4 or more stars'
for b in result_dict['businesses']:
	if b['rating'] >= 4:
		print b['rating'], 'stars\t\t', b['name'] 
		print
