# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-08-29 17:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('directory', '0006_scanresult_no_referrer_policy_set'), ('directory', '0007_auto_20180828_2158')]

    dependencies = [
        ('directory', '0005_directoryentry_delisted'),
    ]

    operations = [
        migrations.AddField(
            model_name='scanresult',
            name='referrer_policy_set_to_no_referrer',
            field=models.NullBooleanField(),
        ),
    ]
