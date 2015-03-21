from rest_framework import mixins, viewsets

from . import models
from . import serializers


class BusinessView(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,  # temporary
                      viewsets.GenericViewSet):
    serializer_class = serializers.BusinessSerializer
    queryset = models.Business.objects.all()  # not used, overridden by get_queryset