from rest_framework import serializers

from panorama.models import Panorama, ReferencePoint, Reference


class ReferencePointSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ReferencePoint
        fields = ("url", "name",
                  "latitude", "longitude", "altitude",
                  "refpoint_references")


class PanoramaSerializer(serializers.HyperlinkedModelSerializer):
    # fixme : return absolute URL for tiles_url
    class Meta:
        model = Panorama
        fields = ("url", "name", "loop", "image_width", "image_height",
                  "latitude", "longitude", "altitude",
                  "tiles_url",
                  "panorama_references")


class ReferenceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reference
        # fixme: a validator is automatically added (see below) but does
        # not seem to be respected.
        # validators =
        # [<UniqueTogetherValidator(queryset=Reference.objects.all(),
        # fields=(u'reference_point', u'panorama'))>]
        fields = ("url", "reference_point", "panorama", "x", "y")
