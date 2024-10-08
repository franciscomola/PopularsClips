# clips/urls.py

from django.urls import path
from .views import clip_list, streamer_clips

urlpatterns = [
    path('', clip_list, name='clip_list'),  # URL para la lista de clips
    path('streamer/<int:streamer_id>/', streamer_clips, name='streamer_clips'),  # URL para clips de un streamer específico
]
