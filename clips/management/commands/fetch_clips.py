import json
from django.core.management.base import BaseCommand
from clips.twitch_api import get_access_token, get_top_clips
from clips.utils import save_clips_to_db

# fetch_clips.py

class Command(BaseCommand):
    help = 'Fetches top clips from Twitch and saves them to the database.'

    def handle(self, *args, **kwargs):
        # Obtén el token de acceso de Twitch
        access_token = get_access_token()
        if not access_token:
            self.stdout.write(self.style.ERROR('Failed to get access token from Twitch.'))
            return

        # Obtén los clips populares filtrando por idioma (español en este caso)
        clips_data = get_top_clips(access_token, language='es')
        if not clips_data:
            self.stdout.write(self.style.ERROR('Failed to fetch clips from Twitch.'))
            return

        # Guarda los clips en la base de datos
        save_clips_to_db(clips_data)
        self.stdout.write(self.style.SUCCESS('Successfully fetched and saved clips to the database.'))


