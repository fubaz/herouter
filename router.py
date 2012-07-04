from flask import Flask, redirect, request, render_template
app = Flask(__name__)
import os
from datetime import datetime

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

class Router(object):
    redirects = {}
    failure_template = "snap.html"

    def __init__(self, redirects=None):
        if redirects:
            if not isinstance(redirects, dict):
                raise TypeError('Router expects a dict of redirects')
            else:
                self.redirects = redirects

        if not db_name in server:
            server.create(db_name)

        self.db = server[db_name]

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
        if hostname in self.db:
            doc = self.db[hostname]
            if 'destination' in doc:
                destination = doc['destination']+'/'+uri

                return redirect(destination)

        if hostname in self.redirects:
            destination = self.redirects[hostname]

            return redirect(destination)

        return render_template(self.failure_template, hostname=hostname, uri=uri)

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
    app.debug = False
    app.run('0.0.0.0', port=port)
