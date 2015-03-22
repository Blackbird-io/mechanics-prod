from rest_framework import mixins, viewsets
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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        question = self.get_object()
        serializer = self.get_serializer(question, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # next_question field is available when a question is answered
        next_question = question.next_question
        if next_question:
            #TODO maybe a redirect?
            return Response(self.get_serializer(next_question).data,
                        status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


    def get_queryset(self):
        return super(QuestionView, self).get_queryset().filter(business=self.kwargs['business_pk'])

