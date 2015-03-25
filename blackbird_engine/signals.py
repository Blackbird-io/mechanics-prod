from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models
from . import interview


def register():
    @receiver(post_save, sender=models.Business, weak=False, dispatch_uid='business')
    def business(sender, instance, created, **kwargs):
        if created:
            instance.next_question = interview.get_next_question(instance)

    @receiver(post_save, sender=models.Question, weak=False, dispatch_uid='question')
    def question(sender, instance, created, **kwargs):
        # TODO check if instance was answered before?
        if instance.response_array:
            # don't delete associated models
            sender.objects.filter(business=instance.business,
                                  sequence_num__gt=instance.sequence_num).delete()
            instance.next_question = interview.get_next_question(instance.business, instance)