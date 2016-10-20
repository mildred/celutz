import requests
import logging

from django.http import HttpResponse, HttpResponseServerError
from django.conf import settings

logger = logging.getLogger(__name__)


def geonames_altitude(request, lat, lon):
    lat = float(lat)
    lon = float(lon)
    url = settings.GEONAMES_ASTERGDEM.format(lat=lat, lon=lon)
    r = requests.get(url)
    if r.status_code != 200:
        return HttpResponseServerError()
    # The API sometimes returns an error but still sends a 200 code,
    # so we validate the answer just to make sure...
    try:
        return HttpResponse(float(r.text))
    except ValueError:
        logger.warning("api.geonames.org error: {}".format(r.text))
        return HttpResponseServerError()
