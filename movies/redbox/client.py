from datetime import datetime
import hashlib
import logging
import re
import urllib
from django.core.exceptions import ObjectDoesNotExist
import requests
from django.conf import settings
from django.core.cache import cache
import time
import unicodedata
from redbox.models import Movie


class Response():
    def __init__(self, status_code, content, size):
        self.status_code = status_code
        self.content = content
        self.size = size
        self.cached = datetime.now()


def fetch(url, **kwargs):
    """ Cache all API calls for an hour"""
    cache_key = hashlib.md5(url).hexdigest()
    response = cache.get(cache_key)
    if response is None:
        api_response = requests.get(url, **kwargs)
        response = Response(api_response.status_code, api_response.json(), len(api_response.text))
        cache.set(cache_key, response, 3600)
        response.cached = None
    if not hasattr(response, 'size'):
        response.size = 0
    return response


def download_movies(out):
    url = "%sproducts/movies?apiKey=%s" % (settings.REDBOX_URL, settings.REDBOX_APIKEY,)
    out.write("Fetching products...", ending='')
    out.flush()
    response = fetch(url,
        headers={
          'Accept': 'application/json',
          'X-Redbox-ApiKey': settings.REDBOX_APIKEY
        },
        timeout=600)
    out.write("complete!")
    movies = response.content
    if 'Products' not in movies or \
                    'Movie' not in movies['Products'] or \
                    len(movies['Products']['Movie']) == 0:
        out.write("Download complete!")
        out.write(response.content)
        return
    for obj in movies['Products']['Movie']:
        time.sleep(1)
        productid = obj['@productId']

        # Fetch or create movie entity
        try:
            movie = Movie.objects.get(productid=productid)
        except ObjectDoesNotExist:
            movie = Movie(productid=productid)

        # Set properties on movie object
        for key in obj:
            if type(obj[key]) != dict:
                if hasattr(movie, key.replace('@','').lower()):
                    setattr(movie, key.replace('@','').lower(), obj[key])
        movie.title = unicode(re.sub(' \(.*\)', '', movie.title))
        #out.write('Fetched %s' % movie.title)
        #if 'RatingContext' in obj and \
        #                '@ratingReason' in obj['RatingContext']:
        #    movie.ratingReason = obj['RatingContext']['@ratingReason']
        if 'Actors' in obj and 'Person' in obj['Actors']:
            movie.actors = ", ".join(obj['Actors']['Person'])
        if 'BoxArtImages' in obj and 'link' in obj['BoxArtImages'] \
                and type(obj['BoxArtImages']['link']) == list \
                and len(obj['BoxArtImages']['link']) >= 3 \
                and '@href' in obj['BoxArtImages']['link'][2]:
            movie.thumb = obj['BoxArtImages']['link'][2]['@href']

        # Don't recalc score if it's really bad
        #if hasattr(movie, 'score') and movie.score < 40 and movie.score > 0:
        #    continue
        movie.score = -1

        # Then look up Rotten Tomatoes scores
        url = "http://www.omdbapi.com/?t=%s&tomatoes=true" \
              % (urllib.quote(unicodedata.normalize('NFKD', movie.title).encode('ascii', 'ignore')))
        if hasattr(movie, 'releaseyear'):
            url += "&y=%s" % (movie.releaseyear)
        response = fetch(url, timeout=600)

        if response.status_code != 200:
            logging.error("Could not retrieve Rotten Tomatoes information for %s: %s" % (obj['Title'], url))
            continue
        else:
            result = response.content
            if 'Response' in result and result['Response'] == 'False':
                out.write('Skipping %s' % movie.title)
                continue

        # This is where the magic happens
        #out.write("Recalculating score for %s" % obj['Title'])
        movie.thumb = result['Poster'] if 'Poster' in result else ''
        try:
            movie.metascore = int(result['Metascore']) if 'Metascore' in result else 0
        except:
            movie.metascore = 0
        try:
            movie.critics_score = int(result['tomatoMeter']) if 'tomatoMeter' in result else 0
        except:
            movie.critics_score = 0
        try:
            movie.critics_consensus = result['tomatoConsensus'] if 'tomatoConsensus' in result else ''
        except:
            movie.critics_consensus = ''
        try:
            movie.audience_score = int(result['tomatoUserMeter']) if 'tomatoUserMeter' in result else 0
        except:
            movie.audience_score = 0
        movie.score = int((movie.metascore + movie.critics_score) / 2)

        if 'Released' in result:
            try:
                movie.releasedate = datetime.strptime(result['Released'], "%d %b %Y")
            except:
                movie.releasedate = None

        # Adjust score based on release date
        try:
            daysago = (datetime.now() - movie.releasedate).days
        except:
            daysago = 90
        movie.daysago = daysago
        if daysago <= 30:
            movie.score += 5
        if daysago <= 7:
            movie.score += 10
        if daysago > 90:
            movie.score -= 20
        if not hasattr(movie, 'score'):
            movie.score = 0

        # Save and return movie
        out.write("{title}\t{metascore}\t{critics_score}\t{audience_score}\t{score}".format(**movie.__dict__))
        movie.save()


def fetch_inventory(zipcode):
    # Fetch inventory for all kiosks within 10 miles
    results = []
    logging.info("Fetching kiosks near %s" % zipcode)
    url = "%sstores/postalcode/%s?apiKey=%s" \
          % (settings.REDBOX_URL, zipcode, settings.REDBOX_APIKEY)
    response = fetch(url, headers={
        'Accept': 'application/json',
        'X-Redbox-ApiKey': settings.REDBOX_APIKEY
    })
    if response.status_code != 200:
        raise ValueError("Could not retrieve kiosks near %s" % zipcode)
    kiosks_root = response.content
    kiosks = kiosks_root['StoreBulkList']['Store']
    num_kiosks = 0
    for kiosk in kiosks:
        num_kiosks += 1
        if num_kiosks > 7:
            continue
        store_id = kiosk['@storeId']
        lat = kiosk['Location'].get('@lat')
        lon = kiosk['Location'].get('@long')
        logging.info("Looking up inventory for store %s,%s" % (lat,lon))
        url = "%sinventory/stores/latlong/%s,%s?apiKey=%s" \
              % (settings.REDBOX_URL, lat, lon, settings.REDBOX_APIKEY)
        response = fetch(url, headers={
            'Accept': 'application/json',
            'X-Redbox-ApiKey': settings.REDBOX_APIKEY
        })
        if response.status_code != 200:
            logging.error("Could not retrieve inventory for store: %s,%s" % (lat,lon))
            continue
        inventory_root = response.content
        for inventory in inventory_root['Inventory']['StoreInventory'][0]['ProductInventory']:
            if inventory['@inventoryStatus'] != "InStock":
                continue
            movie_id = inventory['@productId']
            movie = Movie.get_by_id(movie_id)
            if movie is None:
                # TODO - queue creation
                continue
            if not hasattr(movie, 'score') or not hasattr(movie, 'critics_consensus'):
                movie.key.delete()
                continue
            distance = kiosk.get('DistanceFromSearchLocation')
            output = movie.to_dict()
            output['distance'] = distance
            output['reservation_link'] = "http://www.redbox.com/externalcart?titleID=%s&StoreGUID=%s" % (movie_id.lower(), store_id.lower())
            results.append(output)

    # Generate a unique list of titles, saving closest
    results_keys = {}
    for result in results:
        if result['title'] not in results_keys or \
                        results_keys[result['title']]['distance'] > result['distance']:
            results_keys[result['title']] = result
    unique_results = []
    for result in results_keys:
        unique_results.append(results_keys[result])

    # Sort list by score, truncate list
    unique_results = sorted(unique_results, key=itemgetter('score'), reverse=True)[:50]

    # Persist list to memcache
    cache.set("zipcode-%s" % zipcode, unique_results, 3600)
    cache.set("zipcode-%s-backup" % zipcode, unique_results)
    return unique_results