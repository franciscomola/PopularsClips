import os
import requests
from django.core.management.base import BaseCommand

def get_access_token():
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


def get_user_id(username, access_token):
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


def main():
    """
    Función principal que orquesta la obtención del broadcaster_id.
    """
    # Obtiene el access token
    access_token = get_access_token()

    # Cambia esto al nombre del streamer cuyo broadcaster_id deseas obtener
    username = input("Mete el nombre del usuario que quieras su id:")

    try:
        broadcaster_id = get_user_id(username, access_token)
        print(f'El broadcaster_id para {username} es: {broadcaster_id}')
    except Exception as e:
        print(f'Ocurrió un error: {e}')


if __name__ == "__main__":
    main()
