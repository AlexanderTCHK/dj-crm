# Generated by Django 3.2.5 on 2021-09-14 06:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("leads", "0002_auto_20210913_1833"),
    ]

    operations = [
        migrations.RenameField(
            model_name="user",
            old_name="is_organaizer",
            new_name="is_organizer",
        ),
    ]
