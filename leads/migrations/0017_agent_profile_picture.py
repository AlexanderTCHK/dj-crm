# Generated by Django 3.2.7 on 2021-12-06 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0016_alter_lead_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='profile_picture',
            field=models.ImageField(blank=True, default='agent_picture/unknown-person-profile.jpg', null=True, upload_to='agent_picture/'),
        ),
    ]