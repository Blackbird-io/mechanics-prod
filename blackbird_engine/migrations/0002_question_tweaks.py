# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('blackbird_engine', '0001_v02'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='question_id',
            new_name='bbid',
        ),
        migrations.RemoveField(
            model_name='question',
            name='e_question',
        ),
        migrations.AlterField(
            model_name='question',
            name='progress',
            field=models.IntegerField(default=1),
        ),
    ]
