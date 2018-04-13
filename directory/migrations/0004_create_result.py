# -*- coding: utf-8 -*-
"""
This migrations _only_ creates the Result model in the migration state, not in
the database. The model is created in the database by moving the table from the
landing_page_checker app in landing_page_checker
migration 0011_move_results_model
"""

# Generated by Django 1.11.11 on 2018-04-12 21:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('landing_page_checker', '0011_move_results'),
        ('directory', '0003_auto_20171120_2009'),
    ]

    state_operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('landing_page_domain', models.URLField(db_index=True, max_length=255, verbose_name='Landing page domain name')),
                ('live', models.BooleanField()),
                ('result_last_seen', models.DateTimeField(auto_now_add=True)),
                ('forces_https', models.NullBooleanField()),
                ('hsts', models.NullBooleanField()),
                ('hsts_max_age', models.NullBooleanField()),
                ('hsts_entire_domain', models.NullBooleanField()),
                ('hsts_preloaded', models.NullBooleanField()),
                ('http_status_200_ok', models.NullBooleanField()),
                ('http_no_redirect', models.NullBooleanField()),
                ('expected_encoding', models.NullBooleanField()),
                ('no_server_info', models.NullBooleanField()),
                ('no_server_version', models.NullBooleanField()),
                ('csp_origin_only', models.NullBooleanField()),
                ('mime_sniffing_blocked', models.NullBooleanField()),
                ('noopen_download', models.NullBooleanField()),
                ('xss_protection', models.NullBooleanField()),
                ('clickjacking_protection', models.NullBooleanField()),
                ('good_cross_domain_policy', models.NullBooleanField()),
                ('http_1_0_caching_disabled', models.NullBooleanField()),
                ('cache_control_set', models.NullBooleanField()),
                ('cache_control_revalidate_set', models.NullBooleanField()),
                ('cache_control_nocache_set', models.NullBooleanField()),
                ('cache_control_notransform_set', models.NullBooleanField()),
                ('cache_control_nostore_set', models.NullBooleanField()),
                ('cache_control_private_set', models.NullBooleanField()),
                ('expires_set', models.NullBooleanField()),
                ('safe_onion_address', models.NullBooleanField()),
                ('no_cdn', models.NullBooleanField()),
                ('no_analytics', models.NullBooleanField()),
                ('subdomain', models.NullBooleanField()),
                ('no_cookies', models.NullBooleanField()),
                ('grade', models.CharField(default='?', editable=False, max_length=2)),
                ('securedrop', modelcluster.fields.ParentalKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='results', to='landing_page_checker.SecuredropPage')),
            ],
            options={
                'get_latest_by': 'result_last_seen',
            },
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]