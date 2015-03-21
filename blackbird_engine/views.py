from rest_framework import mixins, viewsets
from rest_framework.decorators import detail_route

from rest_framework import status
from rest_framework.response import Response

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

    @detail_route(methods=['post'])
    def answer(self, request, *args, **kwargs):
        question = self.get_object()
        serializer = serializers.QuestionSerializer(question, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializers.QuestionSerializer(question.next_question).data,
                        status=status.HTTP_201_CREATED)


    def get_queryset(self):
        return super(QuestionView, self).get_queryset().filter(business=self.kwargs['business_pk'])

