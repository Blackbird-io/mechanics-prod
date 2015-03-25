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
        return self.questions.filter(transcribe=True)


class BlackbirdModel(models.Model):
    created_timestamp = timestamp()
    business = models.ForeignKey(Business, related_name="blackbird_models")
    user_context = json_field.JSONField(default=dict)

    complete = models.BooleanField(default=False)

    industry = models.CharField(max_length=256, null=True)
    summary = json_field.JSONField(null=True)
    business_name = models.CharField(max_length=256, null=True)
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
    business = models.ForeignKey(Business, related_name="questions")
    sequence_num = models.PositiveSmallIntegerField()

    # the model that generated this question
    blackbird_model = models.OneToOneField(BlackbirdModel, related_name="question")

    # used by engine
    e_question = json_field.JSONField(null=True)
    question_id = models.CharField(max_length=64, null=True)
    topic_name = models.CharField(max_length=64, null=True)

    # question information.
    progress = models.FloatField(default=0.0)  #TODO validate [0.0, 1.0] range?
    short = models.CharField(max_length=64, null=True)
    prompt = models.TextField(null=True)
    comment = models.TextField(null=True)
    array_caption = models.TextField(null=True)
    input_array = json_field.JSONField(default=list)
    input_type = models.CharField(max_length=64, default='text')  #TODO choices?
    input_sub_type = models.CharField(max_length=64, null=True)  #TODO choices?
    user_can_add = models.BooleanField(default=False)

    #for building business transcript
    transcribe = models.BooleanField(default=False)

    #response data
    response_array = json_field.JSONField(null=True)


class Meta:
    unique_together = ('business', 'sequence_num')
    ordering = ('business', 'sequence_num')
    index_together = ('business', 'transcribe', 'sequence_num')