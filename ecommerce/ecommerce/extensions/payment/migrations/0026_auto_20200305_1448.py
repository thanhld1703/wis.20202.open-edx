# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-03-05 14:48


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0025_card_type_ordering'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Date Created'),
        ),
    ]
