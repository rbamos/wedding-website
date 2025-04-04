# Generated by Django 5.1.1 on 2024-11-30 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('main', '0009_event_about'),
    ]

    operations = [
        migrations.AddField(
            model_name='party',
            name='authentication_token_hash',
            field=models.CharField(default='', max_length=64, unique=True),
        ),
        migrations.AddIndex(
            model_name='party',
            index=models.Index(fields=['authentication_token_hash'], name='main_party_authent_1e2940_idx'),
        ),
    ]
