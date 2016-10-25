# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-18 19:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pois', '0004_auto_20161018_1951'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category_Type',
            fields=[
                ('category_name', models.CharField(max_length=200, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='POI_Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pois.Category_Type')),
                ('poi_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pois.POI')),
            ],
        ),
    ]