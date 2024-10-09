# Generated by Django 4.2.16 on 2024-10-09 19:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Streamer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('twitch_id', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Clip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('url', models.URLField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('twitch_created_at', models.DateTimeField()),
                ('language', models.CharField(choices=[('es', 'Español'), ('en', 'Inglés'), ('fr', 'Francés')], max_length=50)),
                ('from_twitch', models.BooleanField(default=True)),
                ('streamer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clips', to='clips.streamer')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('clip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='clips.clip')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'indexes': [models.Index(fields=['created_at'], name='clips_comme_created_357d07_idx')],
            },
        ),
        migrations.CreateModel(
            name='ClipVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote_value', models.IntegerField()),
                ('voted_at', models.DateTimeField(auto_now_add=True)),
                ('clip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='clips.clip')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'clip')},
            },
        ),
    ]
