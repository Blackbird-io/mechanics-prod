# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BlackbirdModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('complete', models.BooleanField(default=False)),
                ('user_context', json_field.fields.JSONField(default=dict, help_text='Enter a valid JSON object')),
                ('industry', models.CharField(null=True, max_length=256)),
                ('summary',
                 json_field.fields.JSONField(null=True, default='null', help_text='Enter a valid JSON object')),
                ('business_name', models.CharField(null=True, max_length=256)),
                ('tags', json_field.fields.JSONField(null=True, default='null', help_text='Enter a valid JSON object')),
                ('e_model', json_field.fields.JSONField(default='null', help_text='Enter a valid JSON object')),
            ],
            options={
                'ordering': ('-business', '-complete', '-created_timestamp'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('sequence_num', models.PositiveSmallIntegerField(default=0)),
                ('e_question',
                 json_field.fields.JSONField(null=True, default='null', help_text='Enter a valid JSON object')),
                ('question_id', models.CharField(null=True, max_length=64)),
                ('topic_name', models.CharField(null=True, max_length=64)),
                ('progress', models.FloatField(default=0.0)),
                ('short', models.CharField(null=True, max_length=64)),
                ('prompt', models.TextField(null=True)),
                ('comment', models.TextField(null=True)),
                ('array_caption', models.TextField(null=True)),
                ('input_array', json_field.fields.JSONField(default=list, help_text='Enter a valid JSON object')),
                ('input_type', models.CharField(max_length=64, default='text')),
                ('input_sub_type', models.CharField(null=True, max_length=64)),
                ('transcribe', models.BooleanField(default=False)),
                ('response_array',
                 json_field.fields.JSONField(null=True, default='null', help_text='Enter a valid JSON object')),
                (
                'blackbird_model', models.OneToOneField(to='blackbird_engine.BlackbirdModel', related_name='question')),
                ('business', models.ForeignKey(to='blackbird_engine.Business', related_name='questions')),
            ],
            options={
                'ordering': ('business', 'sequence_num'),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='question',
            unique_together=set([('business', 'sequence_num')]),
        ),
        migrations.AlterIndexTogether(
            name='question',
            index_together=set([('business', 'transcribe', 'sequence_num')]),
        ),
        migrations.AddField(
            model_name='blackbirdmodel',
            name='business',
            field=models.ForeignKey(to='blackbird_engine.Business', related_name='blackbird_models'),
            preserve_default=True,
        ),
        migrations.AlterIndexTogether(
            name='blackbirdmodel',
            index_together=set([('business', 'complete', 'created_timestamp')]),
        ),
    ]
