from django.db import models
import json_field


class EngineModel(models.Model):
    e_model = json_field.JSONField(null=True)
    summary = json_field.JSONField(null=True)
    business_name = models.CharField(max_length=256, blank=True)
    code = models.CharField(max_length=256)
    tags = json_field.JSONField(null=True)
