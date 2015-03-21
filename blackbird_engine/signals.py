from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models


def _build_next_question(business, sequence_num=0):
    # TODO create model & question from engine
    model_data, question_data = dict(), dict()
    # TODO if this is last question, update model instead
    bb_model = models.BlackbirdModel.objects.create(business=business, data=model_data)
    question = models.Question.objects.create(business=business,
                                              blackbird_model=bb_model,
                                              sequence_num=sequence_num,
                                              data=question_data)


# TODO make events

def register():
    @receiver(post_save, sender=models.Business, weak=False, dispatch_uid='business')
    def business(sender, instance, created, **kwargs):
        if created:
            _build_next_question(instance)

    @receiver(post_save, sender=models.Question, weak=False, dispatch_uid='question')
    def question(sender, instance, created, **kwargs):
        # TODO check if instance was answered before?
        if instance.answered:
            # TODO also delete model?
            sender.objects.filter(business=instance.business,
                                  sequence_num__gt=instance.sequence_num).delete()
            _build_next_question(instance.business, instance.sequence_num + 1)