# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-14 02:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('productid', models.CharField(db_index=True, max_length=100)),
                ('title', models.CharField(max_length=255)),
                ('releasedate', models.DateField()),
                ('mpaarating', models.CharField(max_length=10)),
                ('thumb', models.URLField(max_length=1024)),
                ('websiteurl', models.URLField(max_length=1024)),
                ('reservation_link', models.URLField(max_length=1024)),
                ('daysago', models.IntegerField()),
                ('metascore', models.IntegerField(help_text='IMDB Metascore')),
                ('audience_score', models.IntegerField()),
                ('critics_score', models.IntegerField()),
                ('critics_consensus', models.TextField()),
                ('synopsislong', models.TextField()),
                ('score', models.IntegerField(help_text='Meta score from algorithm')),
            ],
        ),
    ]
