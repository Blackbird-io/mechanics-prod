from rest_framework import mixins, viewsets

from . import models
from . import serializers


class EngineModelView(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,  # temporary
                      viewsets.GenericViewSet):
    serializer_class = serializers.EngineModelSerializer
    queryset = models.EngineModel.objects.all()  # not used, overridden by get_queryset