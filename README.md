Herouter
========

This is a small flask application that redirects an entire host to a
different domain. This is your tool if you need to direct your
non-www host example.com to www.example.com hosted on GitHub Pages or
another service that does not allow several hosts to be served.

Example
-------

You will best understand the behavior of the application by seeing by
yourself. There are three views:

* [Dashboard](http://dash.herouter.fuk.fi/) in the `HEROKU_HOST`
* [Error page](http://snap.herouter.fuk.fi/) if URL is not
  configured.
* [Redirect](http://www.herouter.fuk.fi/) redirects to this page
  repository

Of course none of this will work if the last build has failed:

[![Build Status](https://ferrix.ci.cloudbees.com/job/Herouter/badge/icon)](https://ferrix.ci.cloudbees.com/job/Herouter/)

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

You can do this from `python` (or `heroku run python`) and configure using
the following functions:

    from router import get_redirect, add_redirect, del_redirect
    add_redirect('example.com', 'http://www.example.com/')
    get_redirect('example.com')
    del_redirect('example.com')

You will need to add incoming addresses to your heroku application as well.

    heroku domains:add example.com

Then you need to follow Heroku's instructions on what to tell your DNS
provider or server.

Debugging
---------

If you want to debug the application, it is best to run it on
localhost. Sadly, that requires some setting up. You will need access
to a CouchDB server and run the following to install the packages
(either in a virtualenv or directly on command line):

    pip install -r requirements.txt

Next, you need to set some environment variables:

    # Instead of redirecting, show the URL
    # Value does not matter, true if defined
    export DEBUG_REDIRECT=a

    # Show errors to user on the browser
    # Value does not matter, true if defined
    export DEBUG=g

    # Database url if something else than http://localhost:5984/
    export CLOUDANT_URL=http://server.com:5984/

    # Show dashboard on URL other than localhost:5000
    export HEROKU_HOST=x

    # If you want to change the port to something else than 5000
    export PORT=4999

By default, the port is 5000 and localhost:5000 is the default
dashboard. So to use localhost to debug redirects, set
`HEROKU_HOST=foo`, `DEBUG_REDIRECT=yes` and run the following
lines in `python`:

    from router import add_redirect
    add_redirect('localhost:5000', 'http://example.com/')

Technical Stuff
---------------

* Flask
* Jinja2
* CouchDB
* WTForms
* Bootstrap

Herouter is (surprisingly) designed to be deployed on a free Heroku
instance.