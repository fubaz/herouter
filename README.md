Herouter
========

This is a small flask application that redirects an entire host to a
different domain. This is your tool if you need to direct your
non-www host example.com to www.example.com hosted on GitHub Pages or
another service that does not allow several hosts to be served.

Deployment
----------

Deploying the application is easy

Create a new Heroku (cedar) app

    git clone http://github.com/ferrix/herouter
    heroku create
    heroku rename myherouter

Add CouchDB service

    heroku addons:add cloudant:oxygen

Configure default dashboard URL

    heroku config:set HEROKU_HOST=myherouter.herokuapp.com

Deploy

    git push heroku master

In case you want to register your hosts with Google Apps or
Webmaster Tools, you should copy the alphanumeric string from the URL
given by the HTML verification method. (eg. google8f7f61119a558993.html)

    heroku config:set GOOGLE_VERIFICATION=8f7f61119a558993

This will make the file appear on all redirected domains.

Configuration
-------------

There is currently no nice way to configure the service from the command
line or web. Luckily CouchDB provides a nice web interface that can be
accessed through Heroku.

    heroku addons:open cloudant

In the user interface create a new database called 'router'. Then create
a document whose `_id` would be the host like `example.com`. Add a field
called `destination` and give it the destination address like
`http://www.example.com`. I recommend putting the protocol part there to
be more explicit. And there you go.

Technical Stuff
---------------

* Flask
* Jinja2
* CouchDB
* WTForms
* Bootstrap

Herouter is (surprisingly) designed to be deployed on a free Heroku
instance.
