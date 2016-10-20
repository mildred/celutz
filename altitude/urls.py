from django.conf.urls import url
from django.views.decorators.cache import cache_page

from altitude.views import geonames_altitude

urlpatterns = [
    url(r'^(?P<lat>-?\d+(?:\.\d+)?)/(?P<lon>-?\d+(?:\.\d+)?)/$', cache_page(7*24*60*60)(geonames_altitude)),
]
