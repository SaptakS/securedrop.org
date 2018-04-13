# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def update_contenttypes(apps, schema_migration):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ContentType.objects.filter(
        app_label='landing_page_checker',
        model='securedropowner'
    ).update(app_label='directory')


def update_contenttypes_reverse(apps, schema_migration):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ContentType.objects.filter(
        app_label='directory',
        model='securedropowner'
    ).update(app_label='landing_page_checker')


class Migration(migrations.Migration):

    dependencies = [
        ('landing_page_checker', '0011_move_results'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    database_operations = [
        migrations.AlterModelTable('SecuredropOwner', 'directory_securedropowner'),
        migrations.RunPython(update_contenttypes, update_contenttypes_reverse),
    ]

    state_operations = [
        migrations.DeleteModel('SecuredropOwner'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations
        )
    ]
