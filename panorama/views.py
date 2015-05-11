# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, DetailView, RedirectView, ListView

from .models import Panorama, ReferencePoint


class PanoramaUpload(CreateView):
    model = Panorama
    fields = ('name', 'image', 'loop', 'latitude', 'longitude', 'altitude')
    template_name = "panorama/new.html"

    def get_success_url(self):
        return reverse_lazy("panorama:gen_tiles", kwargs={"id": self.object.id})

class PanoramaView(DetailView):
    model = Panorama
    template_name = "panorama/view.html"
    context_object_name = "panorama"


class PanoramaGenTiles(RedirectView):
    permanent = False
    pattern_name = "panorama:view_pano"

    def get_redirect_url(self, *args, **kwargs):
        pano = get_object_or_404(Panorama, pk=kwargs['pk'])
        pano.generate_tiles()
        return super(PanoramaGenTiles, self).get_redirect_url(*args, **kwargs)


class PanoramaList(ListView):
    model = Panorama
    template_name = "panorama/list.html"
    context_object_name = "panoramas"
