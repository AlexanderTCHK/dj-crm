# Generated by Django 3.2.7 on 2021-11-25 03:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("leads", "0011_auto_20211123_2000"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="lead",
            name="category",
        ),
        migrations.DeleteModel(
            name="Category",
        ),
    ]
