# utils.py

from clips.models import Clip, Streamer

def save_clips_to_db(clips_data):
    for clip in clips_data:
        # Obtén o crea el streamer
        streamer, _ = Streamer.objects.get_or_create(twitch_id=clip['broadcaster_id'], defaults={'name': clip['broadcaster_name']})

        # Crea el clip
        Clip.objects.create(
            streamer=streamer,
            title=clip['title'],
            url=clip['url'],
            created_at=clip['created_at'],  # Asegúrate de que esta fecha esté en el formato correcto
            language=clip['language'],
            from_twitch=True
        )

