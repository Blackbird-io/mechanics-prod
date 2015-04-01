from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models
from . import interview


def register():
    @receiver(post_save, sender=models.Business, weak=False, dispatch_uid='business')
    def business(sender, instance, created, **kwargs):
        if instance.questions:
            interview.get_next_question(instance)

    @receiver(post_save, sender=models.Question, weak=False, dispatch_uid='question')
    def question(sender, instance, created, **kwargs):
        sender.objects.filter(business=instance.business,
                              sequence_num__gt=instance.sequence_num).delete()
        if instance.response_array is not None:
            instance.next_question = interview.get_next_question(instance.business, instance)