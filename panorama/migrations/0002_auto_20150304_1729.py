# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('panorama', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='panorama',
            name='altitude',
        ),
        migrations.RemoveField(
            model_name='panorama',
            name='id',
        ),
        migrations.RemoveField(
            model_name='panorama',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='panorama',
            name='longitude',
        ),
        migrations.RemoveField(
            model_name='panorama',
            name='name',
        ),
        migrations.AddField(
            model_name='panorama',
            name='referencepoint_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, default=None, serialize=False, to='panorama.ReferencePoint'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='panorama',
            name='image',
            field=models.ImageField(upload_to='pano', verbose_name='image'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='referencepoint',
            name='latitude',
            field=models.FloatField(help_text='In degrees', verbose_name='latitude', validators=[django.core.validators.MinValueValidator(-90), django.core.validators.MaxValueValidator(90)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='referencepoint',
            name='longitude',
            field=models.FloatField(help_text='In degrees', verbose_name='longitude', validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='referencepoint',
            name='name',
            field=models.CharField(help_text='Name of the point', max_length=255, verbose_name='name'),
            preserve_default=True,
        ),
    ]
