# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-19 14:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('landing_page_checker', '0010_auto_20171019_1429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='securedroppage',
            name='organization_logo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='common.CustomImage'),
        ),
    ]
