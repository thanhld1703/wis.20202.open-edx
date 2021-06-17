# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-04-03 11:20


from django.db import migrations

from ecommerce.extensions.refund.constants import REFUND_LIST_VIEW_SWITCH


def create_switch(apps, schema_editor):
    """Create the `enable_refund_list_view` switch if it does not already exist."""
    Switch = apps.get_model('waffle', 'Switch')
    Switch.objects.update_or_create(name=REFUND_LIST_VIEW_SWITCH, defaults={'active': True})


def delete_switch(apps, schema_editor):
    """Delete the `enable_refund_list_view` switch."""
    Switch = apps.get_model('waffle', 'Switch')
    Switch.objects.filter(name=REFUND_LIST_VIEW_SWITCH).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('refund', '0003_auto_20180119_0903'),
    ]

    operations = [
        migrations.RunPython(create_switch, delete_switch),
    ]