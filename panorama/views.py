# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, DetailView, RedirectView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Point, Panorama, ReferencePoint
from .forms import SelectReferencePointForm, CustomPointForm, PanoramaForm


class CelutzLoginMixin(LoginRequiredMixin):
    """Mixin that acts like LoginRequiredMixin if settings.LOGIN_REQUIRED is
    True, and does nothing otherwise.  It allows to choose whether
    accessing celutz requires an account or is open to anybody.
    """
    login_url = '/admin/login/'

    def dispatch(self, request, *args, **kwargs):
        """Small hack: either call our parent (LoginRequiredMixin) or bypass it"""
        if settings.LOGIN_REQUIRED:
            return super(CelutzLoginMixin, self).dispatch(request, *args, **kwargs)
        else:
            return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class PanoramaUpload(CelutzLoginMixin, CreateView):
    model = Panorama
    fields = ('name', 'image', 'loop', 'latitude', 'longitude', 'altitude')
    template_name = "panorama/new.html"

    def get_success_url(self):
        return reverse_lazy("panorama:gen_tiles", kwargs={"pk": self.object.id})


class PanoramaView(CelutzLoginMixin, DetailView):
    model = Panorama
    template_name = "panorama/view.html"
    context_object_name = "panorama"

    def get_context_data(self, **kwargs):
        context = super(PanoramaView, self).get_context_data(**kwargs)
        pano = context['panorama']
        context['panoramas'] = [p for p in Panorama.objects.all() if pano.great_circle_distance(p) <= settings.PANORAMA_MAX_DISTANCE]
        context['poi_list'] = [poi for poi in ReferencePoint.objects.all() if not hasattr(poi, 'panorama') and pano.great_circle_distance(poi) <= settings.PANORAMA_MAX_DISTANCE]
        return context



class PanoramaGenTiles(CelutzLoginMixin, RedirectView):
    permanent = False
    pattern_name = "panorama:view_pano"

    def get_redirect_url(self, *args, **kwargs):
        pano = get_object_or_404(Panorama, pk=kwargs['pk'])
        pano.generate_tiles()
        return super(PanoramaGenTiles, self).get_redirect_url(*args, **kwargs)


class MainView(CelutzLoginMixin, TemplateView):
    template_name = "panorama/main.html"

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context['refpoints_form'] = SelectReferencePointForm
        context['custom_point_form'] = CustomPointForm
        context['newpanorama_form'] = PanoramaForm
        context['panoramas'] = Panorama.objects.all()
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


class LocateReferencePointView(MainView):
    """Displays a located reference point"""
    template_name = 'panorama/locate_point.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        form = SelectReferencePointForm(request.POST)
        if form.is_valid():
            point = form.cleaned_data['reference_point']
            context['located_panoramas'] = self.compute_interesting_panoramas(point)
            context['located_point_name'] = point.name
            context['located_point_lat'] = point.latitude
            context['located_point_lon'] = point.longitude
        return super(LocateReferencePointView, self).render_to_response(context)


class LocateCustomPointView(MainView):
    """Displays a located custom GPS point"""
    template_name = 'panorama/locate_point.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        form = CustomPointForm(request.POST)
        if form.is_valid():
            point = Point(**form.cleaned_data)
            context['located_panoramas'] = self.compute_interesting_panoramas(point)
            context['located_point_lat'] = point.latitude
            context['located_point_lon'] = point.longitude
        return super(LocateCustomPointView, self).render_to_response(context)
