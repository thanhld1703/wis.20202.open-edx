# Generated by Django 1.11.23 on 2019-08-15 15:13


from django.db import migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('publisher', '0078_delete_drupalloaderconfig'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='url_slug',
            field=django_extensions.db.fields.AutoSlugField(blank=True, editable=False, help_text='Leave this field blank to have the value generated automatically.', populate_from='title'),
        ),
    ]