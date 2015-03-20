from django.db import models
import json_field


def timestamp(**kwargs):
    return models.DateTimeField(auto_now_add=True, **kwargs)


class Business(models.Model):
    summary = json_field.JSONField(null=True)
    business_name = models.CharField(max_length=256, blank=True)
    tags = json_field.JSONField(null=True)
    created = timestamp()


class BlackbirdModel(models.Model):
    # business_id passed into engine will be str(business.id)
    business = models.ForeignKey(Business, related_name="blackbird_models")
    data = json_field.JSONField()
    created = timestamp()


class Question(models.Model):
    business = models.ForeignKey(Business, related_name="questions")
    sequence_num = models.PositiveSmallIntegerField()
    data = json_field.JSONField()  # will be populated with answers
    created = timestamp()
    # do we need an "answered" field?

    class Meta:
        unique_together = ('business', 'sequence_num')