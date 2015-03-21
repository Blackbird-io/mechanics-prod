from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models


def _build_next_question(business, prev_question=None):
    sequence_num = prev_question.sequence_num + 1 if prev_question else 0
    # TODO create model & question from engine
    model_data, question_detail = dict(e_model=dict()), \
                                  dict(question_id='Question ' + str(sequence_num))
    # TODO if this is last question, make model complete
    bb_model = models.BlackbirdModel.objects.create(business=business, **model_data)
    return models.Question.objects.create(business=business,
                                          blackbird_model=bb_model,
                                          sequence_num=sequence_num,
                                          detail=question_detail)


def register():
    @receiver(post_save, sender=models.Business, weak=False, dispatch_uid='business')
    def business(sender, instance, created, **kwargs):
        if created:
            instance.next_question = _build_next_question(instance)

    @receiver(post_save, sender=models.Question, weak=False, dispatch_uid='question')
    def question(sender, instance, created, **kwargs):
        # TODO check if instance was answered before?
        if instance.answered:
            # TODO also delete model?
            sender.objects.filter(business=instance.business,
                                  sequence_num__gt=instance.sequence_num).delete()
            instance.next_question = _build_next_question(instance.business, instance)