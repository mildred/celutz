# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('panorama', '0002_auto_20150304_1729'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('x', models.PositiveIntegerField()),
                ('y', models.PositiveIntegerField()),
                ('panorama', models.ForeignKey(related_name='panorama_references', to='panorama.Panorama')),
                ('reference_point', models.ForeignKey(related_name='refpoint_references', to='panorama.ReferencePoint')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='reference',
            unique_together=set([('reference_point', 'panorama')]),
        ),
        migrations.AddField(
            model_name='panorama',
            name='references',
            field=models.ManyToManyField(related_name='referenced_panorama', through='panorama.Reference', to='panorama.ReferencePoint'),
            preserve_default=True,
        ),
    ]
