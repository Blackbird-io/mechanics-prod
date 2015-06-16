import os

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
        return self.current_model.summary

    @property
    def business_name(self):
        return self.current_model.business_name

    @property
    def tags(self):
        return self.current_model.tags

    @property
    def transcript(self):
        return self.questions.filter(transcribe=True, valid=True)

    def __str__(self):
        return '{:d} - {}'.format(self.id, self.business_name)


def model_filename(model, filename):
    return os.path.join(str(model.pk), filename)

class BlackbirdModel(models.Model):
    created_timestamp = timestamp()
    business = models.ForeignKey(Business, related_name="blackbird_models")
    # only use complete models to derive business info
    complete = models.BooleanField(default=False)

    # passed to engine
    user_context = json_field.JSONField(default=dict, blank=True)

    # set by engine, visible to Business
    industry = models.CharField(max_length=256, null=True)
    summary = json_field.JSONField(null=True)
    business_name = models.CharField(max_length=256, null=True)
    tags = json_field.JSONField(null=True)

    # set by engine, hidden from Business
    e_model = models.FileField(upload_to=model_filename, null=True)

    def save(self, *args, **kwargs):
        if self.pk is None:
            e_model_file = self.e_model
            self.e_model = None
            super(BlackbirdModel, self).save(*args, **kwargs)
            self.e_model = e_model_file
            kwargs['force_insert'] = False
            kwargs['force_update'] = True
        super(BlackbirdModel, self).save(*args, **kwargs)

    class Meta:
        index_together = ('business', 'complete', 'created_timestamp')
        ordering = ('-business', '-complete', '-created_timestamp')


class QuestionManager(models.Manager):
    def create_next(self, prev_question=None, end=False, stop=True, **kwargs):
        if prev_question:
            kwargs['business'] = prev_question.business
            kwargs['sequence_num'] = prev_question.sequence_num + 1
        if end:
            kwargs['input_type'] = 'end'
            kwargs['progress'] = 1.0
            if stop:
                kwargs['input_sub_type'] = 'stop'
        return self.create(**kwargs)


class Question(models.Model):
    created_timestamp = timestamp()
    business = models.ForeignKey(Business, related_name="questions")
    sequence_num = models.PositiveSmallIntegerField(default=0)
    # if a question is deleted, it instead becomes invalid to preserve history
    valid = models.BooleanField(default=True)

    # the model that generated this question
    blackbird_model = models.OneToOneField(BlackbirdModel, related_name="question")

    # used by engine
    question_id = models.CharField(max_length=64, null=True)
    topic_name = models.CharField(max_length=64, null=True)

    # question information, passed to portal
    progress = models.IntegerField(default=0)
    short = models.CharField(max_length=64, null=True)
    prompt = models.TextField(null=True)
    comment = models.TextField(null=True)
    array_caption = models.TextField(null=True)
    input_array = json_field.JSONField(default=list)
    input_type = models.CharField(max_length=64, default='text')
    input_sub_type = models.CharField(max_length=64, null=True)
    show_if = json_field.JSONField(null=True)

    # for building business transcript
    transcribe = models.BooleanField(default=False)

    # response data, passed to portal
    response_array = json_field.JSONField(null=True)

    objects = QuestionManager()

    class Meta:
        ordering = ('business', 'valid', 'sequence_num')
        index_together = ('business', 'valid', 'transcribe', 'sequence_num')