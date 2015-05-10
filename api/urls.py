# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function

from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'panoramas', views.PanoramaViewSet)
router.register(r'refpoints', views.ReferencePointViewSet)
router.register(r'references', views.ReferenceViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
#    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
