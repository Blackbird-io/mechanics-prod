from django.contrib import admin

from .models import Business, BlackbirdModel, Question

print('TESTING')
admin.site.register(Business)
admin.site.register(BlackbirdModel)
admin.site.register(Question)