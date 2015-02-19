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


def pano_json(request, pk):
    pano = get_object_or_404(Panorama, pk=pk)
    return JsonResponse(pano.to_dict())

def pano_refpoints(request, pk):
    """Returns the reference points that are close to the given panorama, as a
    JSON object.  Each reference point also includes information relative
    to the given panorama (bearing, elevation, distance).
    """
    pano = get_object_or_404(Panorama, pk=pk)
    refpoints = [r.to_dict_extended(pano) for r in ReferencePoint.objects.all()
                 if r.line_distance(pano) <= settings.PANORAMA_MAX_DISTANCE]
    return JsonResponse(refpoints, safe=False)


class PanoramaGenTiles(RedirectView):
    permanent = False
    pattern_name = "panorama:list"

    def get_redirect_url(self, *args, **kwargs):
        pano = get_object_or_404(Panorama, pk=kwargs['id'])
        pano.generate_tiles()
        return super(PanoramaGenTiles, self).get_redirect_url(*args, **kwargs)


class PanoramaList(ListView):
    model = Panorama
    template_name = "panorama/list.html"
    context_object_name = "panoramas"


