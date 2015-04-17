from django.contrib import admin

from .models import BlackbirdModel, Question


class BlackbirdModelAdmin(admin.ModelAdmin):
    list_filter = ('business', 'complete')
    list_display = ('business', 'complete', 'created_timestamp')


class QuestionAdmin(admin.ModelAdmin):
    list_filter = ('business', 'question_id', 'valid')
    list_display = ('short', 'business', 'valid', 'sequence_num', 'created_timestamp', 'question_id')


admin.site.register(BlackbirdModel, BlackbirdModelAdmin)
admin.site.register(Question, QuestionAdmin)