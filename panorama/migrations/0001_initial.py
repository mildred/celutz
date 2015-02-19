# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Panorama',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('latitude', models.FloatField(help_text='In degrees', verbose_name='latitude')),
                ('longitude', models.FloatField(help_text='In degrees', verbose_name='longitude')),
                ('altitude', models.FloatField(help_text='In meters', verbose_name='altitude', validators=[django.core.validators.MinValueValidator(0.0)])),
                ('name', models.CharField(help_text='Name of the panorama', max_length=255, verbose_name='name')),
                ('loop', models.BooleanField(default=False, help_text='Whether the panorama loops around the edges', verbose_name='360\xb0 panorama')),
                ('image', models.ImageField(upload_to=b'', verbose_name='image')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReferencePoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('latitude', models.FloatField(help_text='In degrees', verbose_name='latitude')),
                ('longitude', models.FloatField(help_text='In degrees', verbose_name='longitude')),
                ('altitude', models.FloatField(help_text='In meters', verbose_name='altitude', validators=[django.core.validators.MinValueValidator(0.0)])),
                ('name', models.CharField(help_text='Name of the reference point', max_length=255, verbose_name='name')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
