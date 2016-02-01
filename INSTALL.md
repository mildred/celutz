Installing celutz
=================

System requirements
-------------------

- Python version 2 (at least 2.6) or version 3 (at least 3.2)
- At least 10 GB of disk space.  You should provision 100 MB for each panorama:
  panoramic pictures can be pretty big to start with, and celutz generates
  a lot of tiles during the initial upload.
- At least 1.5G of RAM, mainly for tile generation.  If you generate tiles on
  another computer, then you need much less, probably as little as 512 MB of
  RAM.  Celutz is a quite simple Django application.
- a fast CPU, again for tile generation.  Having multiple CPU will not be useful
  in most cases, because tile generation is single-threaded.

For reference, generating tiles for a quite large panorama (30000x3487 pixels,
amounting to 105 Mpixels, storing in JPEG) took 855 MB of RAM using Python 3.5
with Pillow 3.0.0 on a x86_64 Linux system.

Installation
------------

Celutz is a fairly standard Django application: refer to the Django
documentation for deployment methods.  The initial installation for development
should look like this:

    # Debian jessie with python3, adapt to your OS
    apt install build-essential python3-dev libjpeg-dev libtiff5-dev zlib1g-dev libopenjp2-7-dev
    virtualenv -p /usr/bin/python3 ~/mycelutzvenv
    . ~/mycelutzvenv/bin/activate
    pip install -r requirements.txt

Configuration
-------------

To configure the application, don't edit `celutz/settings.py` directly, but
instead create a file `celutz/local_settings.py` with your local modifications.

Some things you should (must?) configure:

- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `DEBUG`
- database configuration

Then run the migrations:

    python manage.py migrate

And create a superuser:

    python manage.py createsuperuser

Lastly, you should collect static files to serve them:

    python manage.py collectstatic

Production
----------

One specific information for production usage: you **really** want to serve
the `media/` directory with a real webserver, and **not** with Django itself.
Hundreds of tiles (small image files) will be served from this directory each
time a client visualises a panorama.

You probably also want to configure your webserver to allow to send very large
files in a POST request.  An upper limit of 200 MB should be enough, even for
very large pictures in raw format.

Tile generation
---------------

Tile generation uses Celery, because it is quite a heavy task CPU-wise.

To launch a celery worker while developping, run this in your virtualenv:

    celery -c 1 -A celutz.celery worker --loglevel=info

This tells celery to handle at most one task at a time: `-c 1`.  Indeed,
generating tiles for a single panorama can take quite a lot of RAM.
If you have enough RAM (2GB+) and multiple CPU, you can increase this
parameter to generate tiles for multiple panoramas in parallel.

The default parameters use the Django database as a message queue, to ask
a celery woker to generate tiles for a panorama.  This is far from efficient,
but since there are very few messages, it is not worth the trouble to configure
a real message queue such as RabbitMQ.

Importing reference points
--------------------------

Gathering reference points can be a bit of a hassle.

Some reference points are provided alongside celutz, in `panorama/fixtures`.
To import one set of reference points into the database, run:

    python manage.py loaddata refpoints_mycity

Upgrading from the PHP version of celutz
----------------------------------------

Where you previously using the PHP version of celutz?  You can import all your
old data!  See `UPGRADE.md`.
