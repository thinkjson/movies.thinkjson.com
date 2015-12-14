from django.contrib import admin
from redbox.models import Movie


class MovieAdmin(admin.ModelAdmin):
    ordering = ('-score',)
    list_display = ('title', 'productid', 'metascore', 'critics_score', 'audience_score', 'score', 'format', 'mpaarating',)
    list_filter = ('format', 'mpaarating',)
admin.site.register(Movie, MovieAdmin)
