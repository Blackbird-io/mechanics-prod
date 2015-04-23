from django.http import Http404
from rest_framework import mixins, viewsets
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from . import models
from . import serializers
from . import interview


class BusinessView(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = serializers.BusinessSerializer
    queryset = models.Business.objects.all()

    @detail_route(methods=['post'])
    def landscape_summary(self, request, *args, **kwargs):
        business = self.get_object()
        return Response(interview.get_landscape_summary(business), status=status.HTTP_201_CREATED)

    @detail_route(methods=['post'])
    def forecast(self, request, *args, **kwargs):
        business = self.get_object()
        return Response(interview.get_forecast(business, **request.data), status=status.HTTP_201_CREATED)


class QuestionView(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = models.Question.objects.filter(valid=True)
    lookup_field = 'sequence_num'
    serializer_class = serializers.QuestionSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        question = self.get_object()
        serializer = self.get_serializer(question, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # next_question field is available when a question is answered
        next_question = question.next_question
        return Response(self.get_serializer(next_question).data,
                        status=status.HTTP_201_CREATED)

    @detail_route(methods=['post'])
    def stop(self, request, *args, **kwargs):
        question = self.get_object()
        question.response_array = None
        question.save()
        next_question = interview.stop_interview(question.business, cur_question=question)
        return Response(self.get_serializer(next_question).data,
                        status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        self.get_queryset().filter(sequence_num__gte=instance.sequence_num).update(valid=False)
        if instance.sequence_num == 0:
            interview.get_next_question(instance.business)

    def get_queryset(self):
        # first check that business exists
        if not models.Business.objects.filter(id=self.kwargs['business_pk']).exists():
            raise Http404()
        return super(QuestionView, self).get_queryset().filter(business=self.kwargs['business_pk'])

