# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, DetailView, RedirectView, ListView, TemplateView

from .models import Point, Panorama, ReferencePoint
from .forms import SelectReferencePointForm, CustomPointForm


class PanoramaUpload(CreateView):
    model = Panorama
    fields = ('name', 'image', 'loop', 'latitude', 'longitude', 'altitude')
    template_name = "panorama/new.html"

    def get_success_url(self):
        return reverse_lazy("panorama:gen_tiles", kwargs={"pk": self.object.id})

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


class LocatePointView(TemplateView):
    """View to choose a point to locate (either an existing reference point,
    or from GPS coordinates)"""
    template_name = 'panorama/locate_point.html'

    def get_context_data(self, **kwargs):
        context = super(LocatePointView, self).get_context_data(**kwargs)
        context['refpoints_form'] = SelectReferencePointForm
        context['custom_point_form'] = CustomPointForm
        return context

    def compute_interesting_panoramas(self, point):
        """Compute all panoramas that see the given point, along with the distance
        and direction from each panorama towards the point.  Returns a
        list of (panorama, distance, bearing, elevation) triples.
        """
        if isinstance(point, ReferencePoint):
            queryset = Panorama.objects.exclude(id=point.id)
        else:
            queryset = Panorama.objects
        l = [(pano, pano.line_distance(point), pano.bearing(point), pano.elevation(point))
             for pano in queryset.all() if pano.is_visible(point)]
        # Sort by increasing distance
        return sorted(l, key=lambda x: x[1])


class LocateReferencePointView(LocatePointView):
    """Subclass that handles locating a reference point"""

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        form = SelectReferencePointForm(request.POST)
        context['refpoints_form'] = form
        if form.is_valid():
            point = form.cleaned_data['reference_point']
            context['panoramas'] = self.compute_interesting_panoramas(point)
            context['point_name'] = point.name
        return super(LocateReferencePointView, self).render_to_response(context)


class LocateCustomPointView(LocatePointView):
    """Subclass that handles locating a custom point"""

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        form = CustomPointForm(request.POST)
        context['custom_point_form'] = form
        if form.is_valid():
            point = Point(**form.cleaned_data)
            context['panoramas'] = self.compute_interesting_panoramas(point)
            context['point_lat'] = point.latitude
            context['point_lon'] = point.longitude
        return super(LocateCustomPointView, self).render_to_response(context)
