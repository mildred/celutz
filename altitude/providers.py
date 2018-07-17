# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function

import requests
import logging
import re


logger = logging.getLogger(__name__)


class AltitudeProvider(object):
    url_template = "http://example.com/{lon}/{lat}"

    def parse_answer(self, req):
        """[req] is a Request instances from requests.  Should return a float."""
        try:
            return float(req.text)
        except ValueError:
            raise


class GeonamesProvider(AltitudeProvider):
    url_template = "http://api.geonames.org/astergdem?lat={lat}&lng={lon}&username=celutz&style=full"


class GeoportailProvider(AltitudeProvider):
    url_template = "https://wxs.ign.fr/an7nvfzojv5wa96dsga5nk8w/alti/rest/elevation.xml?lon={lon}&lat={lat}&indent=false&crs=%27CRS:84%27&zonly=true"

    def parse_answer(self, req):
        m = re.search(r'<z>(.*)</z>', req.text)
        if m == None:
            raise ValueError
        return float(m.group(1))


# Main function
def get_altitude(providers, timeout, latitude, longitude):
    """Given a list of altitude provider classes, and a timeout for each
    provider, try them all in order until we obtain a reasonable altitude
    for the given coordinates.

    If all providers fail, returns None.
    """
    # Try all providers in order
    for Provider in providers:
        name = Provider.__name__
        logger.info("Trying {}…".format(name))
        provider = Provider()
        url = provider.url_template.format(lat=latitude, lon=longitude)
        try:
            r = requests.get(url, timeout=timeout)
        except requests.exceptions.ReadTimeout:
            logger.warning("{} timeout out after {} seconds".format(name, timeout))
            continue
        if r.status_code != 200:
            continue
        try:
            alt = provider.parse_answer(r)
            logger.info("Got {}m".format(alt))
            if alt < 0:
                continue
            return alt
        except ValueError:
            continue
    # If all providers failed, return nothing
