import requests, os

#Variables de entorno
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = 'http://localhost'
# Función para obtener el token de acceso de Twitch
def get_access_token():
    url = 'https://id.twitch.tv/oauth2/token'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        print(f"Access Token: {access_token}")  # Asegúrate de que se imprima el token
        return access_token
    else:
        print(f"Error: {response.status_code}, {response.text}")
        response.raise_for_status()

token = get_access_token()
print(f"Access Token: {token}")
# Función para obtener clips populares de Twitch
def get_top_clips(access_token, language=None):
    url = 'https://api.twitch.tv/helix/clips'
    headers = {
        'Authorization': f'Bearer {access_token}',  # Verifica que aquí se envíe correctamente
        'Client-ID': CLIENT_ID
    }
    params = {
        'first': 10,  # Número de clips a obtener
        'language': language  # Filtrado por idioma
    }
    response = requests.get(url, headers=headers, params=params)
    print(f"Request Headers: {headers}")  # Imprime los encabezados para verificar
    response.raise_for_status()
    return response.json().get('data', [])


if __name__ == '__main__':
    # Paso 1: Obtener el token de acceso
    token = get_access_token()
    print(f"Access Token: {token}")

    # Paso 2: Obtener los clips populares
    clips = get_top_clips(token, language='es')  # Clips en español
    for clip in clips:
        print(f"Clip title: {clip['title']}, URL: {clip['url']}")
