# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import json_field.fields


class Migration(migrations.Migration):
    dependencies = [
        ('blackbird_engine', '0002_drop_unique'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blackbirdmodel',
            name='user_context',
            field=json_field.fields.JSONField(blank=True, help_text='Enter a valid JSON object', default=dict),
        ),
    ]
