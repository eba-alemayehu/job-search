# Generated by Django 3.2 on 2024-11-01 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='joblisting',
            name='is_saved',
            field=models.BooleanField(default=False),
        ),
    ]
