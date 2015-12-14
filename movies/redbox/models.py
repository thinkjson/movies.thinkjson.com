from __future__ import unicode_literals

from django.db import models

class Movie(models.Model):
    productid = models.CharField(max_length=100, db_index=True)
    title = models.CharField(max_length=255)
    releasedate = models.DateField(null=True, blank=True)
    mpaarating = models.CharField(max_length=10)
    format = models.CharField(max_length=10, blank=True, null=True)
    thumb = models.URLField(max_length=1024)
    websiteurl = models.URLField(max_length=1024)
    reservation_link = models.URLField(max_length=1024)
    daysago = models.IntegerField(null=True, blank=True)
    metascore = models.IntegerField(help_text='IMDB Metascore')
    audience_score = models.IntegerField()
    critics_score = models.IntegerField()
    critics_consensus = models.TextField()
    synopsislong = models.TextField()
    score = models.IntegerField(help_text='Meta score from algorithm')

    def __unicode__(self):
        return self.title