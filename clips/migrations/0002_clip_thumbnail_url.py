# Generated by Django 4.2.16 on 2024-10-10 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clips', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='clip',
            name='thumbnail_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
