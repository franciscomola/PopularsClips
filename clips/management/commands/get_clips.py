#get_clips
import os
import requests
from django.utils import timezone
from django.core.management.base import BaseCommand
from clips.models import Streamer, Clip

class Command(BaseCommand):
    help = 'Fetch clips from Twitch API and save them to the database'

    def handle(self, *args, **kwargs):
        access_token = self.get_access_token()
        streamers = Streamer.objects.all()  # Obtener todos los streamers de la base de datos
        for streamer in streamers:
            self.stdout.write(self.style.SUCCESS(f'Fetching clips for streamer: {streamer.name}'))
            clips = self.get_clips(access_token, streamer)
            if clips:
                self.stdout.write(self.style.SUCCESS(f'Fetched {len(clips)} clips for {streamer.name}.'))

    def get_access_token(self):
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            'client_id': os.environ.get('CLIENT_ID'),
            'client_secret': os.environ.get('CLIENT_SECRET'),
            'grant_type': 'client_credentials'
        }
        response = requests.post(url, params=params)
        response.raise_for_status()
        return response.json()['access_token']

    def get_clips(self, access_token, streamer):
        url = "https://api.twitch.tv/helix/clips"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Client-Id': os.environ.get('CLIENT_ID'),
        }

        # Parámetros de la API, usando el twitch_id del streamer como broadcaster_id
        params = {
            'broadcaster_id': streamer.twitch_id,
            'first': 100,  # Aumentamos el número para obtener más clips
            'started_at': (timezone.now() - timezone.timedelta(days=30)).isoformat(),
            'ended_at': timezone.now().isoformat(),
        }

        # Hacer la solicitud a la API de Twitch
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            self.stdout.write(self.style.ERROR(f"Error {response.status_code}: {response.text}"))
            return []

        # Obtener los datos de los clips
        clips_data = response.json().get('data', [])

        # Filtrar y ordenar los clips por cantidad de vistas
        sorted_clips = sorted(clips_data, key=lambda x: x.get('view_count', 0), reverse=True)[:5]  # Los 5 más populares

        # Guardar o actualizar los clips en la base de datos
        for clip_data in sorted_clips:
            Clip.objects.update_or_create(
                streamer=streamer,
                url=clip_data['embed_url'],  # Usar la URL de incrustación
                defaults={
                    'title': clip_data['title'],
                    'language': clip_data['language'],
                    'from_twitch': True,
                    'twitch_created_at': clip_data['created_at'],  # Asegúrate de usar el campo correcto
                }
            )

        return sorted_clips

