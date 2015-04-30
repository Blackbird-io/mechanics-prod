from rest_framework import serializers
import dill
from django.core.files.base import ContentFile

from . import models


class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class PickleField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""

    def to_representation(self, value):
        return dill.load(value) if value else None

    # turns into model object
    def to_internal_value(self, data):
        return ContentFile(dill.dumps(data), name='model.pickle')


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


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    # url = QuestionHyperlinkedIdentityField(view_name='question-detail')

    # required=False necessary because of unique_together
    # business = serializers.HyperlinkedRelatedField(required=False, read_only=True, view_name='business-detail')
    sequence_num = serializers.IntegerField(required=False, read_only=True)

    input_array = JSONSerializerField(read_only=True)
    response_array = JSONSerializerField()

    def update(self, instance, validated_data):
        return super(QuestionSerializer, self).update(instance, validated_data)

    def validate(self, data):
        if data['response_array'] and self.instance.input_type == 'end':
            raise serializers.ValidationError('cannot answer end question')
        return data

    class Meta:
        model = models.Question
        read_only_fields = ('created_timestamp', 'sequence_num',
                            'topic_name', 'progress', 'short', 'prompt', 'comment',
                            'array_caption', 'input_array', 'input_type', 'input_sub_type')
        fields = read_only_fields + ('response_array', )


class BusinessSerializer(serializers.HyperlinkedModelSerializer):
    summary = JSONSerializerField(read_only=True)
    tags = JSONSerializerField(read_only=True)
    transcript = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = models.Business
        fields = ('id', 'url', 'industry', 'summary', 'business_name', 'tags', 'transcript')
        read_only_fields = fields


class InternalBlackbirdModelSerializer(serializers.ModelSerializer):
    user_context = JSONSerializerField()
    business_id = serializers.CharField(read_only=True)
    summary = JSONSerializerField(required=False)
    tags = JSONSerializerField(required=False)
    e_model = PickleField()

    class Meta:
        model = models.BlackbirdModel
        fields = ('user_context', 'business_id', 'industry', 'summary',
                  'business_name', 'tags', 'e_model')


class InternalQuestionSerializer(serializers.ModelSerializer):
    e_question = JSONSerializerField()
    input_array = JSONSerializerField()

    class Meta:
        model = models.Question
        fields = ('e_question', 'bbid', 'topic_name', 'progress', 'short',
                  'prompt', 'comment', 'array_caption', 'input_array',
                  'input_type', 'input_sub_type', 'transcribe')