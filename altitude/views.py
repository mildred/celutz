# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseServerError
from django.conf import settings

import altitude.providers


def get_altitude(request, lat, lon):
    lat = float(lat)
    lon = float(lon)
    alt = altitude.providers.get_altitude(settings.ALTITUDE_PROVIDERS,
                                          settings.ALTITUDE_PROVIDER_TIMEOUT,
                                          lat, lon)
    if alt == None:
        return HttpResponseServerError()
    else:
        return HttpResponse(alt)
