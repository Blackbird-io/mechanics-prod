from rest_framework import mixins, viewsets

from . import models
from . import serializers


class BusinessView(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,  # temporary
                   mixins.DestroyModelMixin,  # temporary
                   viewsets.GenericViewSet):
    serializer_class = serializers.BusinessSerializer
    queryset = models.Business.objects.all()


class QuestionView(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):
    queryset = models.Question.objects.all()
    lookup_field = 'sequence_num'
    serializer_class = serializers.QuestionSerializer

    def get_queryset(self):
        return super(QuestionView, self).get_queryset().filter(business=self.kwargs['business_pk'])

