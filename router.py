from flask import Flask, redirect, request, render_template
app = Flask(__name__)
import os
from datetime import datetime
from urllib import urlencode
from urlparse import urlparse, parse_qs

from couchdb.client import Server

google_apps_verify = os.environ.get('GOOGLE_VERIFICATION', None)

dashboards = [
              os.environ.get('HEROKU_HOST', 'localhost:5000'),
             ]

redirects = {
}

couch_url = os.environ.get('CLOUDANT_URL', 'http://localhost:5984/')

server = Server(couch_url)
db_name = 'router'

def get_db(db_name):
    if not db_name in server:
        server.create(db_name)

    return server[db_name]

db = get_db(db_name)

def add_redirect(source, destination, strip_path=False, strip_query=False,
        prefer_destination=False):
    if source in db:
        doc = db[source]
    else:
        doc = {}
    doc['destination']=destination
    doc['strip_path']=strip_path
    doc['strip_query']=strip_query
    doc['prefer_destination']=prefer_destination

    db[source]=doc

def get_redirect(source):
    if source in db:
        return db[source]['destination']
    else:
        return

def del_redirect(source):
    if source in db:
        destination = db[source]['destination']
        del(db[source])
        return destination

class Router(object):
    redirects = {}
    failure_template = "snap.html"

    def __init__(self, redirects=None):
        if redirects:
            if not isinstance(redirects, dict):
                raise TypeError('Router expects a dict of redirects')
            else:
                self.redirects = redirects

        self.db = get_db(db_name)

    def create(self, src, dst):
        self.db[src] = {'destination': dst, 'created': datetime.now()}

    def current_redirects(self):
        ret = []

        for name in self.db:
            destination = self.db[name]['destination']
            ret.append({'source': name.decode('idna'), 'destination': destination.decode('idna')})

        for name in self.redirects.keys():
            ret.append({'source': name.decode('idna'), 'destination': self.redirects['name'].decode('idna')})

        return ret

    def redirect(self, hostname, uri):
        if hostname in self.db and 'destination' in self.db[hostname]:
            destination = self.db[hostname]['destination']
            in_db = True
        elif hostname in self.redirects:
            destination = self.redirects[hostname]
            in_db = False
        else:
            return render_template(self.failure_template, hostname=hostname, uri=uri)

        urlbits = urlparse(destination)

        if not urlbits.netloc:
            urlbits = urlparse('http://' + destination)
            if not urlbits.netloc:
                return render_template(self.failure_template, hostname=hostname, uri=uri)
        scheme = urlbits.scheme or 'http'

        destination = scheme + '://' + urlbits.netloc

        query = {}

        if urlbits.query:
            query = parse_qs(urlbits.query)
            for key, value in query.items():
                query[key] = value[0]
        if request.args and (in_db and not self.db[hostname].get('strip_query')):
            prefer_destination = in_db and self.db[hostname].get('prefer_destination')
            for key, value in request.args.items():
                if key in query and prefer_destination:
                    continue
                query[key] = value
        if query:
            query_string = '?' + urlencode(query)
        else:
            query_string = ''

        if urlbits.fragment:
            fragment = '#' + urlbits.fragment
        else:
            fragment = ''

        if in_db and self.db[hostname].get('strip_path'):
            path = urlbits.path
        else:
            path = '/' + '/'.join([
                                   urlbits.path.strip('/'),
                                   uri.lstrip('/')
                                  ])

        destination += path + query_string + fragment

        if os.environ.get('DEBUG_REDIRECT') and True or False:
            return destination

        return redirect(destination)

rtr = Router(redirects)

class Dash(object):
    urls = []
    template = 'dash.html'

    def __init__(self, urls=None):
        if urls:
            if not isinstance(urls, list):
                raise TypeError('Dash expects a list of urls')
            else:
                self.urls = urls

    def is_dash(self, url):
        return url in self.urls

    def render(self, uri):
        return render_template(self.template, redirects=rtr.current_redirects())

    def __call__(self, uri):
        return self.render(uri)

dash = Dash(dashboards)

@app.route('/_dash/')
@app.route('/_dash/<path:uri>')
def show_dash(uri=None):
    return dash(uri)

@app.route('/')
@app.route('/<path:uri>')
def uri_router(uri=''):
    if google_apps_verify and uri == 'google'+google_apps_verify+'.html':
        return 'google-site-verification: google'+google_apps_verify+'.html'

    hostname = request.host
    
    if dash.is_dash(hostname):
        return dash(uri)

    return rtr.redirect(hostname, uri) 

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.debug = os.environ.get('DEBUG') and True or False
    app.run('0.0.0.0', port=port)
