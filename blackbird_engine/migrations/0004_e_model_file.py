# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

import blackbird_engine.models


class Migration(migrations.Migration):
    dependencies = [
        ('blackbird_engine', '0003_blank_user_context'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blackbirdmodel',
            name='e_model',
        ),
        migrations.AddField(
            model_name='blackbirdmodel',
            name='e_model',
            field=models.FileField(upload_to=blackbird_engine.models.model_filename, null=True),
        ),
    ]
