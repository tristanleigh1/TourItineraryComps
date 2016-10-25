from __future__ import unicode_literals

from django.db import models

class POI(models.Model):
    business_name = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=8, decimal_places=6)
    longitude = models.DecimalField(max_digits=8, decimal_places=6)
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=100)
    num_stars = models.DecimalField(max_digits=2, decimal_places=1)
    num_reviews = models.IntegerField()
    phone_number = models.CharField(max_length=100, null=True)
    price = models.CharField(max_length=5)
    picture_url = models.CharField(max_length=2083, null=True)
    summary = models.TextField()
    
    def __str__(self):
        return self.business_name
    
class Category_Type(models.Model):
    category_name = models.CharField(max_length=200, primary_key=True)
    
    def __str__(self):
        return self.category_name
    
class POI_Type(models.Model):
    category_name = models.ForeignKey('Category_Type',
                                      on_delete=models.CASCADE)
    poi_id = models.ForeignKey('POI', on_delete=models.CASCADE)