# Generated by Django 3.2.7 on 2021-12-09 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0019_followup'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='converted_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
