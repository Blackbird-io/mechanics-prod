from django.db import models
import json_field


def timestamp(**kwargs):
    return models.DateTimeField(auto_now_add=True, **kwargs)


class Business(models.Model):
    # id field is used to call into engine
    created_timestamp = timestamp()
    # generated upon interview completion
    summary = json_field.JSONField(null=True, editable=False)
    business_name = models.CharField(max_length=256, blank=True, editable=False)
    tags = json_field.JSONField(null=True, editable=False)
    transcript = json_field.JSONField(null=True, editable=False)


class BlackbirdModel(models.Model):
    created_timestamp = timestamp()
    # business_id passed into engine will be str(business.id)
    business = models.ForeignKey(Business, related_name="blackbird_models")
    data = json_field.JSONField()

    class Meta:
        index_together = ('business', 'created_timestamp')
        ordering = ('-business', '-created_timestamp')


class Question(models.Model):
    created_timestamp = timestamp()
    business = models.ForeignKey(Business, related_name="questions", editable=False)
    # the model that generated this question
    blackbird_model = models.ForeignKey(BlackbirdModel, related_name="questions", editable=False)
    sequence_num = models.PositiveSmallIntegerField(editable=False)
    #question information.  will also contain response data once answered
    data = json_field.JSONField()
    answered = models.BooleanField(default=False, editable=False)

    class Meta:
        unique_together = ('business', 'sequence_num')
        ordering = ('business', 'sequence_num')