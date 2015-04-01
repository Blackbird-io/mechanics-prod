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
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('complete', models.BooleanField(default=False)),
                ('user_context', json_field.fields.JSONField(help_text='Enter a valid JSON object', default=dict)),
                ('industry', models.CharField(max_length=256, null=True)),
                ('summary',
                 json_field.fields.JSONField(help_text='Enter a valid JSON object', null=True, default='null')),
                ('business_name', models.CharField(max_length=256, null=True)),
                ('tags', json_field.fields.JSONField(help_text='Enter a valid JSON object', null=True, default='null')),
                ('e_model', json_field.fields.JSONField(help_text='Enter a valid JSON object', default='null')),
            ],
            options={
                'ordering': ('-business', '-complete', '-created_timestamp'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('sequence_num', models.PositiveSmallIntegerField(default=0)),
                ('e_question',
                 json_field.fields.JSONField(help_text='Enter a valid JSON object', null=True, default='null')),
                ('question_id', models.CharField(max_length=64, null=True)),
                ('topic_name', models.CharField(max_length=64, null=True)),
                ('progress', models.FloatField(default=0.0)),
                ('short', models.CharField(max_length=64, null=True)),
                ('prompt', models.TextField(null=True)),
                ('comment', models.TextField(null=True)),
                ('array_caption', models.TextField(null=True)),
                ('input_array', json_field.fields.JSONField(help_text='Enter a valid JSON object', default=list)),
                ('input_type', models.CharField(max_length=64, default='text')),
                ('input_sub_type', models.CharField(max_length=64, null=True)),
                ('user_can_add', models.BooleanField(default=False)),
                ('transcribe', models.BooleanField(default=False)),
                ('response_array',
                 json_field.fields.JSONField(help_text='Enter a valid JSON object', null=True, default='null')),
                (
                'blackbird_model', models.OneToOneField(related_name='question', to='blackbird_engine.BlackbirdModel')),
                ('business', models.ForeignKey(related_name='questions', to='blackbird_engine.Business')),
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
            field=models.ForeignKey(related_name='blackbird_models', to='blackbird_engine.Business'),
            preserve_default=True,
        ),
        migrations.AlterIndexTogether(
            name='blackbirdmodel',
            index_together=set([('business', 'complete', 'created_timestamp')]),
        ),
    ]
