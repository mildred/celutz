# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import path, re_path

from .views import MainView, PanoramaUpload, PanoramaView, PanoramaGenTiles, LocateReferencePointView, LocateCustomPointView, CreateReferencePoint

app_name = 'panorama'
urlpatterns = [
    re_path(r'^$', MainView.as_view(), name="main"),
    path('locate_refpoint/', LocateReferencePointView.as_view(), name="locate_refpoint"),
    path('locate_custompoint/', LocateCustomPointView.as_view(), name="locate_custompoint"),
    path('pano/new/', PanoramaUpload.as_view(), name="new"),
    path('refpoint/new/', CreateReferencePoint.as_view(), name="new_refpoint"),
    path('pano/view/<int:pk>/', PanoramaView.as_view(), name="view_pano"),
    path('pano/gen_tiles/<int:pk>/', PanoramaGenTiles.as_view(), name="gen_tiles"),
]
