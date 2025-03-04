import streamlit as st
import requests
import base64
import json
import time
import pandas as pd
from urllib.parse import urlencode

# Spotify API bağlantısı için bilgiler
# Gerçek bir uygulamada, bu bilgileri güvenli bir şekilde saklamalısınız
# Bu değerleri Spotify Developer Dashboard'dan alabilirsiniz
# https://developer.spotify.com/dashboard/applications

SPOTIFY_CLIENT_ID = "YOUR_CLIENT_ID"  # Kendi client ID'nizi buraya girin
SPOTIFY_CLIENT_SECRET = "YOUR_CLIENT_SECRET"  # Kendi client secret'ınızı buraya girin
SPOTIFY_REDIRECT_URI = "YOUR_REDIRECT_URI"  # Spotify Developer Dashboard'da tanımladığınız yönlendirme URI'sı

class SpotifyAPI:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None
        self.token_expiry = 0
    
    def get_auth_url(self):
        """Spotify yetkilendirmesi için URL oluşturur"""
        auth_endpoint = "https://accounts.spotify.com/authorize"
        auth_params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": "user-read-private user-read-email user-top-read playlist-modify-public streaming"
        }
        return f"{auth_endpoint}?{urlencode(auth_params)}"
    
    def get_token(self, auth_code=None):
        """Yetkilendirme kodu ile erişim belirteci alır veya mevcut belirtecin süresini kontrol eder"""
        current_time = time.time()
        
        # Belirteç yoksa veya süresi dolmuşsa yeni belirteç al
        if not self.access_token or current_time >= self.token_expiry:
            if auth_code:
                # Yetkilendirme kodu kullanarak belirteç al
                token_endpoint = "https://accounts.spotify.com/api/token"
                token_data = {
                    "grant_type": "authorization_code",
                    "code": auth_code,
                    "redirect_uri": self.redirect_uri
                }
                
                # Client ID ve Client Secret ile temel yetkilendirme
                client_creds = f"{self.client_id}:{self.client_secret}"
                client_creds_b64 = base64.b64encode(client_creds.encode()).decode()
                
                token_headers = {
                    "Authorization": f"Basic {client_creds_b64}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                
                # Belirteç isteği gönder
                token_response = requests.post(token_endpoint, data=token_data, headers=token_headers)
                token_info = token_response.json()
                
                if "access_token" in token_info:
                    self.access_token = token_info["access_token"]
                    self.token_expiry = current_time + token_info["expires_in"]
                    return True
                return False
            else:
                # İstemci kimlik bilgileriyle belirteç al (kullanıcı yetkilendirmesi olmadan)
                token_endpoint = "https://accounts.spotify.com/api/token"
                token_data = {
                    "grant_type": "client_credentials"
                }
                
                # Client ID ve Client Secret ile temel yetkilendirme
                client_creds = f"{self.client_id}:{self.client_secret}"
                client_creds_b64 = base64.b64encode(client_creds.encode()).decode()
                
                token_headers = {
                    "Authorization": f"Basic {client_creds_b64}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                
                # Belirteç isteği gönder
                token_response = requests.post(token_endpoint, data=token_data, headers=token_headers)
                token_info = token_response.json()
                
                if "access_token" in token_info:
                    self.access_token = token_info["access_token"]
                    self.token_expiry = current_time + token_info["expires_in"]
                    return True
                return False
        
        return True
    
    def search_tracks(self, query, limit=10):
        """Spotify'da şarkı araması yapar"""
        if not self.get_token():
            return []
        
        search_endpoint = "https://api.spotify.com/v1/search"
        search_params = {
            "q": query,
            "type": "track",
            "limit": limit
        }
        
        search_headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        search_response = requests.get(f"{search_endpoint}?{urlencode(search_params)}", headers=search_headers)
        search_results = search_response.json()
        
        if "tracks" in search_results and "items" in search_results["tracks"]:
            tracks = []
            for item in search_results["tracks"]["items"]:
                track = {
                    "id": item["id"],
                    "name": item["name"],
                    "artist": ", ".join([artist["name"] for artist in item["artists"]]),
                    "album": item["album"]["name"],
                    "image_url": item["album"]["images"][0]["url"] if item["album"]["images"] else None,
                    "preview_url": item["preview_url"],
                    "external_url": item["external_urls"]["spotify"]
                }
                tracks.append(track)
            return tracks
        
        return []
    
    def get_audio_features(self, track_id):
        """Şarkının ses özelliklerini alır (danceability, energy, vb.)"""
        if not self.get_token():
            return None
        
        audio_features_endpoint = f"https://api.spotify.com/v1/audio-features/{track_id}"
        
        audio_features_headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        audio_features_response = requests.get(audio_features_endpoint, headers=audio_features_headers)
        audio_features = audio_features_response.json()
        
        return audio_features
    
    def get_recommendations(self, seed_tracks=None, seed_artists=None, seed_genres=None, 
                           target_danceability=None, target_energy=None, target_valence=None, 
                           limit=10):
        """Verilen tohum değerlerine dayalı şarkı önerileri alır"""
        if not self.get_token():
            return []
        
        recommendations_endpoint = "https://api.spotify.com/v1/recommendations"
        recommendations_params = {
            "limit": limit
        }
        
        # Tohum değerlerini ekle
        if seed_tracks:
            recommendations_params["seed_tracks"] = ",".join(seed_tracks[:5])  # Maksimum 5 tohum şarkı
        
        if seed_artists:
            recommendations_params["seed_artists"] = ",".join(seed_artists[:5])  # Maksimum 5 tohum sanatçı
        
        if seed_genres:
            recommendations_params["seed_genres"] = ",".join(seed_genres[:5])  # Maksimum 5 tohum tür
        
        # Hedef özellikleri ekle
        if target_danceability is not None:
            recommendations_params["target_danceability"] = target_danceability
        
        if target_energy is not None:
            recommendations_params["target_energy"] = target_energy
        
        if target_valence is not None:
            recommendations_params["target_valence"] = target_valence
        
        recommendations_headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        recommendations_response = requests.get(
            f"{recommendations_endpoint}?{urlencode(recommendations_params)}", 
            headers=recommendations_headers
        )
        recommendations_results = recommendations_response.json()
        
        if "tracks" in recommendations_results:
            tracks = []
            for item in recommendations_results["tracks"]:
                track = {
                    "id": item["id"],
                    "name": item["name"],
                    "artist": ", ".join([artist["name"] for artist in item["artists"]]),
                    "album": item["album"]["name"],
                    "image_url": item["album"]["images"][0]["url"] if item["album"]["images"] else None,
                    "preview_url": item["preview_url"],
                    "external_url": item["external_urls"]["spotify"]
                }
                tracks.append(track)
            return tracks
        
        return []

def get_genre_recommendations(mood):
    """Ruh haline göre Spotify türleri önerir"""
    mood_genres = {
        "Çok Mutlu": ["happy", "pop", "dance", "disco", "party"],
        "Mutlu": ["pop", "funk", "soul", "dance", "indie-pop"],
        "Keyifli": ["acoustic", "indie", "chill", "folk", "ambient"],
        "Melankolik": ["indie", "classical", "ambient", "study", "piano"],
        "Üzgün": ["sad", "acoustic", "indie", "piano", "classical"]
    }
    
    return mood_genres.get(mood, ["pop", "rock", "indie", "electronic", "classical"])

def mood_to_audio_features(mood):
    """Ruh haline göre Spotify ses özelliklerini belirler"""
    mood_features = {
        "Çok Mutlu": {"danceability": 0.8, "energy": 0.8, "valence": 0.9},
        "Mutlu": {"danceability": 0.7, "energy": 0.7, "valence": 0.7},
        "Keyifli": {"danceability": 0.6, "energy": 0.5, "valence": 0.6},
        "Melankolik": {"danceability": 0.4, "energy": 0.3, "valence": 0.4},
        "Üzgün": {"danceability": 0.3, "energy": 0.3, "valence": 0.2}
    }
    
    return mood_features.get(mood, {"danceability": 0.5, "energy": 0.5, "valence": 0.5})

def find_spotify_tracks(track_names, artist_names, spotify_api):
    """Veri setimizdeki şarkıları Spotify'da arar"""
    spotify_tracks = []
    
    for track, artist in zip(track_names, artist_names):
        # Şarkı adı ve sanatçıyı birleştirerek ara
        query = f"track:{track} artist:{artist}"
        search_results = spotify_api.search_tracks(query, limit=1)
        
        if search_results:
            spotify_tracks.append(search_results[0])
    
    return spotify_tracks

def get_spotify_recommendations_for_mood(mood, spotify_api, limit=5):
    """Verilen ruh haline göre Spotify önerileri alır"""
    # Ruh haline göre tür ve özellik parametreleri belirle
    genres = get_genre_recommendations(mood)
    audio_features = mood_to_audio_features(mood)
    
    # Spotify önerilerini al
    recommendations = spotify_api.get_recommendations(
        seed_genres=genres,
        target_danceability=audio_features["danceability"],
        target_energy=audio_features["energy"],
        target_valence=audio_features["valence"],
        limit=limit
    )
    
    return recommendations

def display_spotify_track(track):
    """Spotify şarkısını görüntüler"""
    # Şarkı kartı oluştur
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if track["image_url"]:
            st.image(track["image_url"], width=100)
        else:
            st.write("🎵")
    
    with col2:
        st.markdown(f"**{track['name']}**")
        st.write(f"Sanatçı: {track['artist']}")
        st.write(f"Albüm: {track['album']}")
        
        # Önizleme URL'si varsa ses oynatıcı ekle
        if track["preview_url"]:
            st.audio(track["preview_url"], format="audio/mp3")
        
        # Spotify bağlantısı ekle
        st.markdown(f"[Spotify'da Aç]({track['external_url']})")

def spotify_recommendations_component(mood, spotify_data=None, limit=5):
    """Ruh haline göre Spotify önerileri bileşeni"""
    st.write("## 🎵 Spotify Müzik Önerileri")
    
    # Spotify API'yi başlat
    spotify_api = SpotifyAPI(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI)
    
    # Spotify API'ye erişim kontrolü
    if not spotify_api.get_token():
        st.error("Spotify API'ye bağlanılamadı. Lütfen API kimlik bilgilerinizi kontrol edin.")
        return
    
    # Önerilen şarkıları göster
    if spotify_data is not None and not spotify_data.empty:
        # Veri setimizden şarkıları Spotify'da bul
        st.write("### Veri Setinizden Önerilen Şarkılar")
        
        # Şarkı ve sanatçı bilgilerini al
        track_names = spotify_data['track_name'].tolist()
        artist_names = spotify_data['artist(s)_name'].tolist()
        
        # Spotify'da arama yap
        spotify_tracks = find_spotify_tracks(track_names, artist_names, spotify_api)
        
        # Şarkıları görüntüle
        for track in spotify_tracks:
            display_spotify_track(track)
    
    # Spotify API'den doğrudan önerilen şarkılar
    st.write("### Spotify'dan Önerilen Şarkılar")
    recommendations = get_spotify_recommendations_for_mood(mood, spotify_api, limit)
    
    if recommendations:
        for track in recommendations:
            display_spotify_track(track)
    else:
        st.info("Bu ruh haline uygun Spotify önerisi bulunamadı.")

def get_available_genres(spotify_api):
    """Spotify'da mevcut türleri alır"""
    if not spotify_api.get_token():
        return []
    
    genres_endpoint = "https://api.spotify.com/v1/recommendations/available-genre-seeds"
    
    genres_headers = {
        "Authorization": f"Bearer {spotify_api.access_token}"
    }
    
    genres_response = requests.get(genres_endpoint, headers=genres_headers)
    genres_results = genres_response.json()
    
    if "genres" in genres_results:
        return genres_results["genres"]
    
    return []
