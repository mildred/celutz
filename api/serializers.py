from rest_framework import serializers

from panorama.models import Panorama, ReferencePoint

class PanoramaSerializer(serializers.HyperlinkedModelSerializer):
    # fixme : return absolute URL for tiles_url
    class Meta:
        model = Panorama
        fields = ("url", "name", "loop",
                  "latitude", "longitude", "altitude",
                  "tiles_url")

class ReferencePointSerializer(serializers.HyperlinkedModelSerializer):
    # fixme : return absolute URL for tiles_url
    class Meta:
        model = ReferencePoint
        fields = ("url", "name",
                  "latitude", "longitude", "altitude")

