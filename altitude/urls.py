# -*- coding: utf-8 -*-

from django.urls import re_path
from django.views.decorators.cache import cache_page

from altitude.views import get_altitude

app_name = 'altitude'
urlpatterns = [
    re_path(r'^(?P<lat>-?\d+(?:\.\d+)?)/(?P<lon>-?\d+(?:\.\d+)?)/$', cache_page(7*24*60*60)(get_altitude)),
]
