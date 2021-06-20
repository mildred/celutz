from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('altitude/', include('altitude.urls', namespace="altitude")),
    path('', include('panorama.urls', namespace="panorama")),
    path('api/v1/', include('api.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
# In debug mode, serve tiles
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
