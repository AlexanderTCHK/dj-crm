# Generated by Django 3.2.7 on 2021-09-29 12:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("leads", "0006_auto_20210929_1518"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="category",
            name="organization",
        ),
    ]
