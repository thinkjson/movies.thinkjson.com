from django.core.management.base import BaseCommand
from redbox.client import download_movies


class Command(BaseCommand):
    help = 'Downloads the movie list from Redbox'

    def handle(self, *args, **options):
        download_movies(out=self.stdout)