# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function

from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'panoramas', views.PanoramaViewSet)
router.register(r'refpoints', views.ReferencePointViewSet)
router.register(r'references', views.ReferenceViewSet)

urlpatterns = [
    path('', include(router.urls)),
#    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
