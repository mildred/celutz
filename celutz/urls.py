from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'celutz.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('panorama.urls', namespace="panorama")),
    url(r'^api/v1/', include('api.urls')),
# In debug mode, serve tiles
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
