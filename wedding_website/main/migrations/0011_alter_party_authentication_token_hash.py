# Generated by Django 5.1.1 on 2024-12-01 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_party_authentication_token_hash_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='party',
            name='authentication_token_hash',
            field=models.CharField(default=None, max_length=64, null=True, unique=True),
        ),
    ]
