# Generated by Django 1.11.3 on 2017-10-02 17:05


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_metadata', '0058_auto_course_about_page_creation_switch'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='prerequisites_raw',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='course',
            name='syllabus_raw',
            field=models.TextField(blank=True, null=True),
        ),
    ]
