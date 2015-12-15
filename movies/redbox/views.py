from django.shortcuts import render, redirect
from django.core.cache import cache
from redbox.client import fetch_inventory


def index(request):
    # If zip code entered, without javascript working,
    # we'll receive the zip code here. Let's handle that
    # and redirect to the proper place:
    zip_code = request.GET.get('zip')
    if zip_code and re.match(r'^\d{5}$', zip_code):
        # TODO: Default 302 okay? Otherwise, set 'permanent=True'.
        # TODO: URL/Route duplication. Need to use named route:
        return redirect('/{zip_code}'.format(zip_code=zip_code))

    response = render(request, 'index.html')
    response['Cache-Control'] = 'public, max-age=3600'
    return response

def zipcode(request, zipcode):
    results = cache.get("zipcode-%s" % zipcode)
    if results is None:
        results = fetch_inventory(zipcode)
        cache.set("zipcode-%s" % zipcode, results, 3600)

    template_values = {"results": results,
                       "zipcode": zipcode}
    response = render(request, 'zipcode.html', template_values)
    response['Cache-Control'] = 'public, max-age=3600'
    return response

