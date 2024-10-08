import os
import requests
from django.core.management.base import BaseCommand
from clips.models import Streamer  # Asegúrate de importar tu modelo Streamer correctamente

class Command(BaseCommand):
    help = 'Obtiene el broadcaster_id de un streamer dado su nombre de usuario y lo guarda en la base de datos.'

    def get_access_token(self):
        """
        Obtiene el access token para realizar solicitudes a la API de Twitch.
        """
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            'client_id': os.environ.get('CLIENT_ID'),
            'client_secret': os.environ.get('CLIENT_SECRET'),
            'grant_type': 'client_credentials'
        }
        response = requests.post(url, params=params)
        response.raise_for_status()  # Lanza un error si la respuesta es un error
        return response.json()['access_token']

    def get_user_id(self, username, access_token):
        """
        Obtiene el broadcaster_id de un streamer dado su nombre de usuario.
        """
        url = "https://api.twitch.tv/helix/users"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Client-Id': os.environ.get('CLIENT_ID'),
        }
        params = {
            'login': username,  # Nombre de usuario del streamer
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Lanza un error si la respuesta es un error
        data = response.json()

        if data['data']:
            return data['data'][0]['id']  # Devuelve el broadcaster_id
        else:
            raise ValueError("No se encontró el usuario.")

    def save_streamer(self, username, broadcaster_id):
        """
        Guarda el streamer en la base de datos. Si ya existe, actualiza su ID.
        """
        streamer, created = Streamer.objects.update_or_create(
            name=username,
            defaults={'twitch_id': broadcaster_id}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Se creó un nuevo streamer: {streamer.name} con ID: {streamer.twitch_id}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'El streamer {streamer.name} ya existía, se actualizó su ID: {streamer.twitch_id}'))

    def handle(self, *args, **options):
        """
        Función principal que orquesta la obtención del broadcaster_id.
        """
        access_token = self.get_access_token()
        username = input("Mete el nombre del usuario que quieras su id: ")

        try:
            broadcaster_id = self.get_user_id(username, access_token)
            self.stdout.write(self.style.SUCCESS(f'El broadcaster_id para {username} es: {broadcaster_id}'))
            self.save_streamer(username, broadcaster_id)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ocurrió un error: {e}'))

