# Generated by Django 3.2.7 on 2021-12-06 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0017_agent_profile_picture'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agent',
            name='profile_picture',
        ),
        migrations.AddField(
            model_name='user',
            name='user_picture',
            field=models.ImageField(default='agent_picture/unknown-person-profile.jpg', upload_to='agent_picture/'),
        ),
        migrations.AlterField(
            model_name='lead',
            name='profile_picture',
            field=models.ImageField(default='profile_picture/unknown-person-profile.jpg', upload_to='profile_picture/'),
        ),
    ]
