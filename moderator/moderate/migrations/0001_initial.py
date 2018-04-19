# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=400)),
                ('archived', models.BooleanField(default=False)),
                ('slug', models.SlugField(max_length=400, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='MozillianProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(max_length=100, blank=True)),
                ('username', models.CharField(max_length=40)),
                ('avatar_url', models.URLField(default=b'', max_length=400)),
                ('user', models.OneToOneField(related_name='userprofile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['username'],
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.TextField(validators=[django.core.validators.MaxLengthValidator(280), django.core.validators.MinLengthValidator(10)])),
                ('answer', models.TextField(default=b'', blank=True, validators=[django.core.validators.MaxLengthValidator(280)])),
                ('addressed', models.BooleanField(default=False)),
                ('asked_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('event', models.ForeignKey(related_name='questions', to='moderate.Event')),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_voted', models.DateField(auto_now_add=True)),
                ('question', models.ForeignKey(related_name='votes', to='moderate.Question')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([('user', 'question')]),
        ),
    ]
