import requests
from decouple import config
from django.utils.timezone import now, timedelta
from django.core.management.base import BaseCommand
from clips.models import Streamer, Clip

class Command(BaseCommand):
    help = 'Fetch clips from Twitch API and save them to the database'

    def handle(self, *args, **kwargs):
        access_token = self.get_access_token()
        streamers = Streamer.objects.all()

        for streamer in streamers:
            self.stdout.write(self.style.SUCCESS(f'Fetching clips for streamer: {streamer.name}'))
            try:
                clips = self.get_clips(access_token, streamer)
                if clips:
                    self.stdout.write(self.style.SUCCESS(f'Fetched and saved {len(clips)} clips for {streamer.name}.'))
                else:
                    self.stdout.write(self.style.WARNING(f'No clips found for {streamer.name}.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error fetching clips for {streamer.name}: {e}'))

    def get_access_token(self):
        """
        Obtiene el token de acceso para la API de Twitch.
        """
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            'client_id': config('TWITCH_CLIENT_ID'),  # Carga desde el archivo .env
            'client_secret': config('TWITCH_CLIENT_SECRET'),  # Carga desde el archivo .env
            'grant_type': 'client_credentials'
        }
        response = requests.post(url, data=params)
        response.raise_for_status()
        return response.json()['access_token']

    def get_clips(self, access_token, streamer):
        """
        Obtiene los clips de Twitch de un streamer específico.
        """
        url = "https://api.twitch.tv/helix/clips"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Client-Id': config('TWITCH_CLIENT_ID'),
        }

        # Rango de fechas: últimos 30 días
        started_at = (now() - timedelta(days=30)).isoformat()
        ended_at = now().isoformat()
        params = {
            'broadcaster_id': streamer.twitch_id,
            'first': 100,
            'started_at': started_at,
            'ended_at': ended_at,
        }

        all_clips = []
        while True:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            clips_data = data.get('data', [])
            all_clips.extend(clips_data)

            # Manejo de paginación
            pagination = data.get('pagination', {}).get('cursor')
            if not pagination:
                break
            params['after'] = pagination

        # Filtrar y guardar los 5 clips más populares
        top_clips = sorted(all_clips, key=lambda x: x.get('view_count', 0), reverse=True)[:5]
        for clip_data in top_clips:
            Clip.objects.update_or_create(
                streamer=streamer,
                url=clip_data['embed_url'],  # Usa 'url' para guardar el enlace principal
                defaults={
                    'title': clip_data['title'],
                    'language': clip_data['language'],
                    'from_twitch': True,
                    'twitch_created_at': clip_data['created_at'],
                }
            )

        return top_clips
