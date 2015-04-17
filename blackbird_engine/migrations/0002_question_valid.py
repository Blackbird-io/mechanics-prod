# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blackbird_engine', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ('business', 'valid', 'sequence_num')},
        ),
        migrations.AddField(
            model_name='question',
            name='valid',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterUniqueTogether(
            name='question',
            unique_together=set([('business', 'valid', 'sequence_num')]),
        ),
        migrations.AlterIndexTogether(
            name='question',
            index_together=set([('business', 'valid', 'transcribe', 'sequence_num')]),
        ),
    ]
