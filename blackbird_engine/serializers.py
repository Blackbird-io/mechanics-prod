from rest_framework import serializers

from . import models


class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class BusinessSerializer(serializers.HyperlinkedModelSerializer):
    summary = JSONSerializerField(read_only=True)
    tags = JSONSerializerField(read_only=True)
    transcript = JSONSerializerField(read_only=True)

    class Meta:
        model = models.Business


# TODO make e_model available somehow for admin


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        models = models.Business