from django.shortcuts import render

def index():
    # If zip code entered, without javascript working,
    # we'll receive the zip code here. Let's handle that
    # and redirect to the proper place:
    zip_code = self.request.GET.get('zip')
    if zip_code and re.match(r'^\d{5}$', zip_code):
        # TODO: Default 302 okay? Otherwise, set 'permanent=True'.
        # TODO: URL/Route duplication. Need to use named route:
        return self.redirect('/{zip_code}'.format(zip_code=zip_code))
    template_values = {}
    if self.request.get('loading') != '':
        template = jinja_environment.get_template('templates/loading.html')
    else:
        template = jinja_environment.get_template('templates/index.html')
        self.response.headers['Cache-Control'] = 'public, max-age=3600'
    self.response.out.write(template.render(template_values))

def zipcode():
    results = memcache.get("zipcode-%s" % zipcode)
    if results is None or results == "loading":
        backup_results = memcache.get("zipcode-%s-backup" % zipcode)
        if results != "loading":
            memcache.set("zipcode-%s" % zipcode, "loading", time=3600)
            deferred.defer(fetch_inventory, zipcode)
        if backup_results is None:
            template = jinja_environment.get_template(
                'templates/loading.html')
            self.response.out.write(template.render({}))
            return
        else:
            results = backup_results

    template_values = {"results": results,
                       "zipcode": zipcode}
    template = jinja_environment.get_template('templates/zipcode.html')
    self.response.out.write(template.render(template_values))
    self.response.headers['Cache-Control'] = 'public, max-age=3600'

