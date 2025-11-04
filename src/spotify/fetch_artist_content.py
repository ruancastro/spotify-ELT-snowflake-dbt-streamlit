from token_manager import TokenManager
from os import getenv
import os
import re
import requests
from typing import Optional
from utils.load_env import load_env

def _extract_artist_id_from_url(url: str) -> Optional[str]:
    if not url:
        return None
    m = re.search(r"artist/([A-Za-z0-9]+)", url)
    return m.group(1) if m else None

def fetch_artist_content(token:str, artist_id:str) -> dict:
    """Fetch artist content from Spotify API.
    """

    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    # exemplo de uso: usa LINK_TUE do .env se presente
    try:
        load_env(env_path=r'.env')
        token_manager = TokenManager(client_id=getenv("CLIENT_ID"),
                                     client_secret=getenv("CLIENT_SECRET"))
        token = token_manager.get_new_token()
        artist = fetch_artist_content(token=token, artist_id=getenv("LINK_TUE"))
        print(artist)
    except Exception as e:
        print("Erro ao buscar artista:", e)