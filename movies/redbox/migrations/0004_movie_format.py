# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-14 12:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('redbox', '0003_auto_20151214_0245'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='format',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
