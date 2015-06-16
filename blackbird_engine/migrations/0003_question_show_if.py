# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import json_field.fields


class Migration(migrations.Migration):
    dependencies = [
        ('blackbird_engine', '0002_question_tweaks'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='show_if',
            field=json_field.fields.JSONField(help_text='Enter a valid JSON object', default=None, blank=True,
                                              null=True),
        ),
    ]
