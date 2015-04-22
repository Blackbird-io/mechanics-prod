# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('blackbird_engine', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='question',
            unique_together=set([]),
        ),
    ]
