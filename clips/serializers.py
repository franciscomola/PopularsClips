#serializers.py
from rest_framework import serializers
from .models import Clip, Streamer
class StreamerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Streamer
        fields = ['id', 'name', 'twitch_id', 'created_at']

class ClipSerializer(serializers.ModelSerializer):
    streamer = StreamerSerializer(read_only=True)  # Relación con Streamer

    class Meta:
        model = Clip
        fields = ['id', 'title', 'url', 'thumbnail_url', 'twitch_created_at', 'language', 'streamer']


