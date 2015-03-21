from rest_framework import serializers

from . import models


class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class QuestionUrlMixin():
    def get_question_url(self, obj, view_name, request, format):
        kwargs = {
            'business_pk': obj.business_id,
            'sequence_num': obj.sequence_num
        }
        return self.reverse(view_name, kwargs=kwargs, request=request, format=format)


class QuestionHyperlinkedRelatedField(serializers.HyperlinkedRelatedField, QuestionUrlMixin):
    def get_url(self, *args, **kwargs):
        return self.get_question_url(*args, **kwargs)


class QuestionHyperlinkedIdentityField(serializers.HyperlinkedIdentityField, QuestionUrlMixin):
    def get_url(self, *args, **kwargs):
        return self.get_question_url(*args, **kwargs)


class BusinessSerializer(serializers.HyperlinkedModelSerializer):
    summary = JSONSerializerField(read_only=True)
    tags = JSONSerializerField(read_only=True)
    transcript = JSONSerializerField(read_only=True)
    questions = QuestionHyperlinkedRelatedField(read_only=True, many=True, view_name='question-detail')

    class Meta:
        model = models.Business


# TODO make e_model available somehow for admin


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    data = JSONSerializerField()
    url = QuestionHyperlinkedIdentityField(view_name='question-detail')
    business = serializers.HyperlinkedRelatedField(required=False, read_only=True, view_name='business-detail')
    sequence_num = serializers.IntegerField(required=False, read_only=True)

    class Meta:
        model = models.Question
        fields = ('url', 'business', 'sequence_num', 'created_timestamp', 'data')
