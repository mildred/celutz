# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('panorama', '0003_auto_20150310_1853'),
    ]

    operations = [
        migrations.AddField(
            model_name='panorama',
            name='image_height',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='panorama',
            name='image_width',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='panorama',
            name='image',
            field=models.ImageField(height_field='image_height', upload_to='pano', width_field='image_width', verbose_name='image'),
            preserve_default=True,
        ),
    ]
