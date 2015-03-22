from django.db import models
import json_field


def timestamp(**kwargs):
    return models.DateTimeField(auto_now_add=True, **kwargs)


class Business(models.Model):
    # id field is used to call into engine
    created_timestamp = timestamp()
    # generated upon interview completion

    @property
    def current_model(self):
        if not hasattr(self, '_current_model'):
            try:
                self._current_model = BlackbirdModel.objects.filter(business=self, complete=True)[0]
            except IndexError:
                self._current_model = BlackbirdModel()
        return self._current_model

    @property
    def industry(self):
        return self.current_model.industry

    @property
    def summary(self):
        return self.current_model.industry

    @property
    def business_name(self):
        return self.current_model.business_name

    @property
    def tags(self):
        return self.current_model.tags

    @property
    def transcript(self):
        return [question.data for question in self.questions.all() if question.transcribe]


class BlackbirdModel(models.Model):
    created_timestamp = timestamp()
    business = models.ForeignKey(Business, related_name="blackbird_models")
    user_context = json_field.JSONField(default=dict)

    complete = models.BooleanField(default=False)

    industry = models.CharField(max_length=256, blank=True)
    summary = json_field.JSONField(null=True)
    business_name = models.CharField(max_length=256, blank=True)
    tags = json_field.JSONField(null=True)

    e_model = json_field.JSONField()
    # only use complete models to derive business info

    @property
    def business_alias(self):
        return str(self.business_id)

    class Meta:
        index_together = ('business', 'complete', 'created_timestamp')
        ordering = ('-business', '-complete', '-created_timestamp')


class Question(models.Model):
    created_timestamp = timestamp()
    business = models.ForeignKey(Business, related_name="questions", editable=False)
    # the model that generated this question
    blackbird_model = models.ForeignKey(BlackbirdModel, related_name="questions", editable=False)
    sequence_num = models.PositiveSmallIntegerField(editable=False)
    # question information.  will also contain response data once answered
    detail = json_field.JSONField()
    answered = models.BooleanField(default=False, editable=False)


class Meta:
    unique_together = ('business', 'sequence_num')
    ordering = ('business', 'sequence_num')