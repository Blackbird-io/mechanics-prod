from rest_framework import serializers

from . import models


class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


# TODO make e_model available somehow
class EngineModelSerializer(serializers.HyperlinkedModelSerializer):
    summary = JSONSerializerField()
    tags = JSONSerializerField()

    class Meta:
        model = models.EngineModel
        fields = ('id', 'summary', 'business_name', 'code', 'tags')