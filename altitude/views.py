import urllib

from django.http import HttpResponse
from django.conf import settings


def geonames_altitude(request, lat, lon):
    lat = float(lat)
    lon = float(lon)
    url = settings.GEONAMES_ASTERGDEM.format(lat=lat, lon=lon)
    return HttpResponse(urllib.request.urlopen(url))
