# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-05 21:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0007_directorypage_faq_link'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResultGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Will be displayed as the group heading.', max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ResultState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('name', models.CharField(help_text='Must be a field in the landing_page_checker.Result model.', max_length=255)),
                ('success_text', wagtail.wagtailcore.fields.RichTextField()),
                ('failure_text', wagtail.wagtailcore.fields.RichTextField()),
                ('is_warning', models.BooleanField(help_text='If checked, will display a flag and yellow text. If left unchecked, will display an x and red text.')),
                ('fix_text', wagtail.wagtailcore.fields.RichTextField(blank=True, null=True)),
                ('result_group', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='result_states', to='directory.ResultGroup')),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
        ),
    ]