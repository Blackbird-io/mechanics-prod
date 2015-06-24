# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DbFile',
            fields=[
                ('name', models.CharField(max_length=512, primary_key=True, serialize=False)),
                ('blob', models.BinaryField()),
                ('size', models.IntegerField()),
                ('accessed', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
