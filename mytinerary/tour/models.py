from __future__ import unicode_literals

from django.db import models

'''
    A POI object represents a point of interest as obtained from Yelp.
'''
class POI(models.Model):

    def default_category():
        return "None"
    business_name = models.CharField(max_length=400)
    latitude = models.DecimalField(max_digits=30, decimal_places=17)
    longitude = models.DecimalField(max_digits=30, decimal_places=17)
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=100)
    num_stars = models.DecimalField(max_digits=2, decimal_places=1)
    num_reviews = models.IntegerField()
    phone_number = models.CharField(max_length=100, null=True)
    price = models.CharField(max_length=5)
    picture_url = models.CharField(max_length=2083, null=True)
    category = models.CharField(max_length=100)
    popularity = models.DecimalField(max_digits=7, decimal_places=4)
    summary = models.CharField(max_length=3000)

    def __str__(self):
        return self.business_name
