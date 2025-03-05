import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.express as px

# Sayfa yapılandırması
st.set_page_config(
    page_title="MindMingle Veri Testi",
    page_icon="🧠",
    layout="wide"
)

# Başlık
st.title("🧠 MindMingle Veri Testi")

# Veri setlerini yükleme ve kontrol
st.header("1. Veri Seti Kontrolü")

try:
    # Netflix verisi yükleme
    st.subheader("Netflix Veri Seti")
    netflix_data = pd.read_csv('netflix.csv')
    st.success(f"Netflix veri seti başarıyla yüklendi. {len(netflix_data)} satır ve {len(netflix_data.columns)} sütun.")
    
    # Netflix veri yapısını göster
    with st.expander("Netflix Veri Yapısı"):
        st.write("İlk 5 satır:")
        st.dataframe(netflix_data.head())
        
        st.write("Sütun İsimleri:")
        st.write(netflix_data.columns.tolist())
        
        # İçerik türleri kontrolü
        if 'listed_in' in netflix_data.columns:
            st.write("İçerik Türleri Örnekleri:")
            st.write(netflix_data['listed_in'].sample(10).tolist())
        else:
            st.error("'listed_in' sütunu bulunamadı.")
    
    # Spotify verisi yükleme
    st.subheader("Spotify Veri Seti")
    spotify_data = pd.read_csv('spotify.csv', encoding="ISO-8859-1", sep=",")
    st.success(f"Spotify veri seti başarıyla yüklendi. {len(spotify_data)} satır ve {len(spotify_data.columns)} sütun.")
    
    # Spotify veri yapısını göster
    with st.expander("Spotify Veri Yapısı"):
        st.write("İlk 5 satır:")
        st.dataframe(spotify_data.head())
        
        st.write("Sütun İsimleri:")
        st.write(spotify_data.columns.tolist())
        
        # Gerekli sütunların kontrolü
        required_columns = ['danceability_%', 'energy_%', 'valence_%', 'acousticness_%']
        missing_columns = [col for col in required_columns if col not in spotify_data.columns]
        
        if missing_columns:
            st.error(f"Aşağıdaki gerekli sütunlar eksik: {missing_columns}")
        else:
            st.success("Tüm gerekli sütunlar mevcut.")
except Exception as e:
    st.error(f"Veri yükleme hatası: {e}")
    st.info("Veri setlerinin doğru formatta ve doğru konumda olduğundan emin olun.")

# Filtreleme ve öneri testleri
st.header("2. Filtreleme Testi")

mood_options = ["Çok Mutlu", "Mutlu", "Keyifli", "Melankolik", "Üzgün"]
test_mood = st.selectbox("Test edilecek ruh halini seçin:", mood_options)

if st.button("Filtreleme Testi Yap"):
    try:
        # Netflix filtreleme testi
        st.subheader("Netflix Filtreleme Testi")
        
        # Filtreleme koşullarını belirle
        if test_mood == "Çok Mutlu" or test_mood == "Mutlu":
            condition = netflix_data['listed_in'].str.contains("Comedy") | netflix_data['listed_in'].str.contains("Animation")
        elif test_mood == "Üzgün":
            condition = netflix_data['listed_in'].str.contains("Drama") | netflix_data['listed_in'].str.contains("Romantic") | netflix_data['listed_in'].str.contains("Comedy")
        elif test_mood == "Keyifli":
            condition = netflix_data['listed_in'].str.contains("Family") | netflix_data['listed_in'].str.contains("Documentary") | netflix_data['listed_in'].str.contains("Animation")
        elif test_mood == "Melankolik":
            condition = netflix_data['listed_in'].str.contains("Art House") | netflix_data['listed_in'].str.contains("Independent") | netflix_data['listed_in'].str.contains("Drama")
        
        # Filtrelenmiş veriyi göster
        filtered_netflix = netflix_data[condition]
        filtered_count = len(filtered_netflix)
        
        if filtered_count > 0:
            st.success(f"{filtered_count} film/dizi bulundu.")
            sample_size = min(5, filtered_count)
            st.write(f"Rastgele {sample_size} öneri:")
            st.dataframe(filtered_netflix.sample(sample_size)[['title', 'listed_in', 'description']])
        else:
            st.warning("Bu ruh haline uygun içerik bulunamadı.")
        
        # Spotify filtreleme testi
        st.subheader("Spotify Filtreleme Testi")
        
        # Eksik sütunları kontrol et
        if 'danceability_%' not in spotify_data.columns or 'energy_%' not in spotify_data.columns or 'valence_%' not in spotify_data.columns:
            st.error("Gerekli sütunlar eksik. Spotify veritabanının doğru olduğundan emin olun.")
        else:
            # Filtreleme koşullarını belirle
            if test_mood in ["Çok Mutlu", "Mutlu"]:
                # Yüksek dans edilebilirlik ve pozitif değerler
                condition = (spotify_data['danceability_%'] > 70) & (spotify_data['valence_%'] > 70)
            elif test_mood == "Üzgün":
                # Düşük enerji, düşük valence - daha sakin ve duygusal müzikler
                condition = (spotify_data['energy_%'] < 50) & (spotify_data['valence_%'] < 50)
            elif test_mood == "Keyifli":
                # Orta enerji, yüksek akustik - keyifli ve rahatlatıcı müzikler
                condition = (spotify_data['energy_%'].between(50, 70)) & (spotify_data['acousticness_%'] > 50)
            elif test_mood == "Melankolik":
                # Yüksek akustik, düşük enerji - derin ve düşündürücü müzikler
                condition = (spotify_data['acousticness_%'] > 60) & (spotify_data['energy_%'] < 60)
            
            # Filtrelenmiş veriyi göster
            filtered_spotify = spotify_data[condition]
            filtered_count = len(filtered_spotify)
            
            if filtered_count > 0:
                st.success(f"{filtered_count} şarkı bulundu.")
                sample_size = min(5, filtered_count)
                st.write(f"Rastgele {sample_size} öneri:")
                st.dataframe(filtered_spotify.sample(sample_size)[['track_name', 'artist(s)_name', 'danceability_%', 'energy_%', 'valence_%']])
            else:
                st.warning("Bu ruh haline uygun şarkı bulunamadı.")
    except Exception as e:
        st.error(f"Filtreleme hatası: {e}")
        st.info("Hata detaylarını inceleyerek veri yapısı veya filtreleme mantığındaki sorunları tespit edebilirsiniz.")

# Elle veri seti sütun isimlerini düzenleme seçeneği
st.header("3. Veri Seti Sütun İsimleri Düzenleme")

if st.checkbox("Sütun isimlerini düzenlemek ister misiniz?"):
    st.info("Veri setindeki sütun isimlerini analizlerinize uygun hale getirmek için kullanabilirsiniz.")
    
    try:
        # Netflix sütunlarını düzenleme
        st.subheader("Netflix Sütunları")
        netflix_columns = netflix_data.columns.tolist()
        
        st.write("Mevcut sütunlar:")
        for i, col in enumerate(netflix_columns):
            st.write(f"{i+1}. {col}")
            
        # Örnek bir sütun değiştirme
        old_netflix_col = st.selectbox("Değiştirilecek Netflix sütunu:", netflix_columns)
        new_netflix_col = st.text_input("Yeni sütun ismi:")
        
        if st.button("Netflix Sütununu Değiştir"):
            if new_netflix_col:
                netflix_data = netflix_data.rename(columns={old_netflix_col: new_netflix_col})
                st.success(f"'{old_netflix_col}' sütunu '{new_netflix_col}' olarak değiştirildi.")
                st.write("Güncellenmiş sütunlar:")
                st.write(netflix_data.columns.tolist())
        
        # Spotify sütunlarını düzenleme
        st.subheader("Spotify Sütunları")
        spotify_columns = spotify_data.columns.tolist()
        
        st.write("Mevcut sütunlar:")
        for i, col in enumerate(spotify_columns):
            st.write(f"{i+1}. {col}")
            
        # Örnek bir sütun değiştirme
        old_spotify_col = st.selectbox("Değiştirilecek Spotify sütunu:", spotify_columns)
        new_spotify_col = st.text_input("Yeni sütun ismi:")
        
        if st.button("Spotify Sütununu Değiştir"):
            if new_spotify_col:
                spotify_data = spotify_data.rename(columns={old_spotify_col: new_spotify_col})
                st.success(f"'{old_spotify_col}' sütunu '{new_spotify_col}' olarak değiştirildi.")
                st.write("Güncellenmiş sütunlar:")
                st.write(spotify_data.columns.tolist())
    except Exception as e:
        st.error(f"Sütun düzenleme hatası: {e}")

# Örnek statik öneriler
st.header("4. Statik Öneri Demosu")
st.info("Bu bölüm, veri setlerinden bağımsız olarak çalışan statik öneriler göstermektedir.")

demo_mood = st.selectbox("Demo ruh hali:", mood_options, key="demo_mood")

if st.button("Statik Önerileri Göster"):
    # Statik film önerileri
    st.subheader("🎬 Film Önerileri")
    
    # Ruh haline göre örnek filmler
    film_demos = {
        "Çok Mutlu": [
            {"title": "Inside Out", "type": "Animation, Comedy", "description": "Genç bir kızın duygularının kişileştirilmiş hikayeleri."},
            {"title": "La La Land", "type": "Musical, Romance", "description": "Los Angeles'ta geçen müzikal bir aşk hikayesi."},
            {"title": "The Grand Budapest Hotel", "type": "Comedy, Adventure", "description": "Ünlü bir otel müdürü ve lobicinin hikayesi."}
        ],
        "Mutlu": [
            {"title": "Forrest Gump", "type": "Drama, Comedy", "description": "Düşük IQ'lu bir adamın olağanüstü yaşam yolculuğu."},
            {"title": "The Intouchables", "type": "Comedy, Drama", "description": "Zengin bir adamla bakıcısı arasındaki beklenmedik dostluk."},
            {"title": "Big Fish", "type": "Adventure, Fantasy", "description": "Bir baba ile oğlu arasındaki geç gelen uzlaşma hikayesi."}
        ],
        "Keyifli": [
            {"title": "The Secret Life of Walter Mitty", "type": "Adventure, Comedy", "description": "Sıradan bir adamın olağanüstü hayallerle dolu hikayesi."},
            {"title": "Chef", "type": "Comedy, Drama", "description": "Bir şefin kendi yolunu çizme hikayesi."},
            {"title": "About Time", "type": "Drama, Fantasy", "description": "Zamanı kontrol edebilen bir adamın dokunaklı hikayesi."}
        ],
        "Melankolik": [
            {"title": "Lost in Translation", "type": "Drama, Romance", "description": "Tokyo'da yolları kesişen iki yalnız ruhun hikayesi."},
            {"title": "Eternal Sunshine of the Spotless Mind", "type": "Drama, Romance", "description": "Anılarını sildirmeye çalışan eski sevgililerin hikayesi."},
            {"title": "Her", "type": "Drama, Romance", "description": "Bir adam ve yapay zeka asistanı arasındaki ilişki."}
        ],
        "Üzgün": [
            {"title": "The Pursuit of Happyness", "type": "Biography, Drama", "description": "Bir baba ve oğlunun zorluklara karşı mücadelesi."},
            {"title": "Good Will Hunting", "type": "Drama", "description": "Sorunlu bir dahinin terapi yolculuğu."},
            {"title": "The Shawshank Redemption", "type": "Drama", "description": "Umut ve dayanıklılık üzerine bir hapishane hikayesi."}
        ]
    }
    
    for film in film_demos.get(demo_mood, []):
        st.markdown(f"""
        <div style="background-color:#f9f9f9; border-radius:10px; padding:15px; margin-bottom:15px;">
            <h4>{film['title']}</h4>
            <p><b>Tür:</b> {film['type']}</p>
            <p>{film['description']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Statik müzik önerileri
    st.subheader("🎵 Müzik Önerileri")
    
    # Ruh haline göre örnek şarkılar
    music_demos = {
        "Çok Mutlu": [
            {"name": "Happy", "artist": "Pharrell Williams", "features": "Dans: 82%, Enerji: 84%, Pozitiflik: 96%"},
            {"name": "Can't Stop the Feeling!", "artist": "Justin Timberlake", "features": "Dans: 72%, Enerji: 67%, Pozitiflik: 93%"},
            {"name": "Uptown Funk", "artist": "Mark Ronson ft. Bruno Mars", "features": "Dans: 86%, Enerji: 91%, Pozitiflik: 85%"}
        ],
        "Mutlu": [
            {"name": "Good as Hell", "artist": "Lizzo", "features": "Dans: 76%, Enerji: 70%, Pozitiflik: 81%"},
            {"name": "Don't Start Now", "artist": "Dua Lipa", "features": "Dans: 77%, Enerji: 73%, Pozitiflik: 77%"},
            {"name": "Blinding Lights", "artist": "The Weeknd", "features": "Dans: 75%, Enerji: 73%, Pozitiflik: 75%"}
        ],
        "Keyifli": [
            {"name": "Sunday Morning", "artist": "Maroon 5", "features": "Dans: 68%, Enerji: 52%, Pozitiflik: 67%"},
            {"name": "Put Your Records On", "artist": "Corinne Bailey Rae", "features": "Dans: 61%, Enerji: 57%, Pozitiflik: 65%"},
            {"name": "Banana Pancakes", "artist": "Jack Johnson", "features": "Dans: 54%, Enerji: 51%, Pozitiflik: 62%"}
        ],
        "Melankolik": [
            {"name": "Skinny Love", "artist": "Bon Iver", "features": "Dans: 42%, Enerji: 36%, Pozitiflik: 41%"},
            {"name": "Gravity", "artist": "John Mayer", "features": "Dans: 45%, Enerji: 38%, Pozitiflik: 42%"},
            {"name": "To Build a Home", "artist": "The Cinematic Orchestra", "features": "Dans: 37%, Enerji: 34%, Pozitiflik: 36%"}
        ],
        "Üzgün": [
            {"name": "Someone Like You", "artist": "Adele", "features": "Dans: 33%, Enerji: 30%, Pozitiflik: 28%"},
            {"name": "Fix You", "artist": "Coldplay", "features": "Dans: 36%, Enerji: 29%, Pozitiflik: 25%"},
            {"name": "Hurt", "artist": "Johnny Cash", "features": "Dans: 31%, Enerji: 29%, Pozitiflik: 22%"}
        ]
    }
    
    for music in music_demos.get(demo_mood, []):
        st.markdown(f"""
        <div style="background-color:#f9f9f9; border-radius:10px; padding:15px; margin-bottom:15px;">
            <h4>{music['name']}</h4>
            <p><b>Sanatçı:</b> {music['artist']}</p>
            <p>{music['features']}</p>
        </div>
        """, unsafe_allow_html=True)
