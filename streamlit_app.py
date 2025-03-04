import streamlit as st
import pandas as pd
import numpy as np
import time
import os
import json
from datetime import datetime
import plotly.express as px

# Özel modülleri içe aktar
from face_emotion import emotion_detector_component
from user_auth import init_user_system, login_page, save_user_mood_history, get_user_mood_history, add_to_favorites, get_user_favorites
from spotify_integration import spotify_recommendations_component
from podcast_youtube import podcast_youtube_component

# Veri setlerini yükleme
@st.cache_data
def load_data():
    netflix_data = pd.read_csv('netflix.csv')  # Netflix veri seti
    spotify_data = pd.read_csv('spotify.csv', encoding="ISO-8859-1", sep=",")  # Spotify veri seti
    books_data = pd.read_csv('books.csv')  # Kitap veri seti
    return netflix_data, spotify_data, books_data

# Ruh hali analizi fonksiyonları
def calculate_mood(feeling_score, activity_score, energy_level, social_interaction):
    total_score = feeling_score + activity_score + energy_level + social_interaction
    if total_score >= 30:
        return "Çok Mutlu"
    elif 20 <= total_score < 30:
        return "Mutlu"
    elif 15 <= total_score < 20:
        return "Keyifli"
    elif 10 <= total_score < 15:
        return "Melankolik"
    else:
        return "Üzgün"

def filter_netflix_by_mood(data, mood):
    """Ruh haline göre Netflix içeriklerini filtreler"""
    if mood == "Çok Mutlu" or mood == "Mutlu":
        filtered_data = data[data['listed_in'].str.contains("Comedy") | data['listed_in'].str.contains("Animation")]
    elif mood == "Üzgün":
        filtered_data = data[data['listed_in'].str.contains("Drama") | data['listed_in'].str.contains("Romantic") | data['listed_in'].str.contains("Comedy")]
    elif mood == "Keyifli":
        filtered_data = data[data['listed_in'].str.contains("Family") | data['listed_in'].str.contains("Documentary") | data['listed_in'].str.contains("Animation")]
    elif mood == "Melankolik":
        filtered_data = data[
            data['listed_in'].str.contains("Art House") | data['listed_in'].str.contains("Independent") | data['listed_in'].str.contains("Drama")]
    return filtered_data.sample(n=min(5, len(filtered_data)))

def filter_spotify_by_mood(data, mood):
    """Ruh haline göre Spotify müziklerini filtreler"""
    if mood in ["Çok Mutlu", "Mutlu"]:
        # Yüksek dans edilebilirlik ve pozitif değerler
        mood_mask = (data['danceability_%'] > 70) & (data['valence_%'] > 70)
    elif mood == "Üzgün":
        # Düşük enerji, düşük valence - daha sakin ve duygusal müzikler
        mood_mask = (data['energy_%'] < 50) & (data['valence_%'] < 50)
    elif mood == "Keyifli":
        # Orta enerji, yüksek akustik - keyifli ve rahatlatıcı müzikler
        mood_mask = (data['energy_%'].between(50, 70)) & (data['acousticness_%'] > 50)
    elif mood == "Melankolik":
        # Yüksek akustik, düşük enerji - derin ve düşündürücü müzikler
        mood_mask = (data['acousticness_%'] > 60) & (data['energy_%'] < 60)
    
    filtered_data = data[mood_mask]
    
    if len(filtered_data) >= 5:
        return filtered_data.sample(n=5)
    else:
        return data.sample(n=5)  # Yeterli sonuç bulunamazsa rastgele 5 şarkı döndür

def filter_books_by_mood(data, mood):
    """Ruh haline göre kitapları filtreler"""
    # Bu fonksiyon, kitap veri setinin yapısına bağlı olarak ayarlanmalıdır
    # Örnek bir filtreleme:
    return data.sample(n=5)  # Şimdilik rastgele 5 kitap döndürüyoruz

def generate_mood_chart(feeling, activity, energy_level, social_interaction):
    """Ruh hali için radar grafiği oluşturur"""
    categories = ['Mutluluk', 'Aktivite', 'Enerji', 'Sosyal Etkileşim']
    values = [feeling, activity, energy_level, social_interaction]
    
    fig = px.line_polar(
        r=values,
        theta=categories,
        line_close=True,
        range_r=[0, 10],
        title="Ruh Hali Analiz Grafiği"
    )
    fig.update_traces(fill='toself')
    return fig

def main():
    # Sayfa yapılandırması
    st.set_page_config(
        page_title="MindMingle v2.0",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS stilleri
    st.markdown("""
    <style>
    .big-font {
        font-size:35px !important;
        font-weight: bold;
        text-align: center;
        margin: 20px;
        color: #4A90E2;
    }
    .subtitle {
        font-size:22px !important;
        text-align: center;
        margin: 10px;
        color: #5A6C8D;
    }
    .card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    .card:hover {
        transform: translateY(-5px);
    }
    .highlight {
        color: #4CAF50;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 18px;
        margin: 12px 0;
        border: none;
        cursor: pointer;
        border-radius: 8px;
        font-size: 16px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    .tabs {
        margin-top: 20px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 5px;
        background-color: #f0f2f6;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Başlık
    st.markdown('<div class="big-font">🧠 MINDMINGLE 2.0 🎵🎬📚</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Ruh Halinize Göre Kişiselleştirilmiş Öneri Platformu</div>', unsafe_allow_html=True)
    
    # Yan panel
    st.sidebar.image("logo.png", use_column_width=True)
    st.sidebar.title("EUREKA")
    st.sidebar.write("Ekip Üyeleri:")
    st.sidebar.write("- Aycan Karaçanta Kurt")
    st.sidebar.write("- Can Umurhan Öksüz")
    st.sidebar.write("- Kadir Alçin")
    st.sidebar.write("- Meryem Tarhan Özkul")
    st.sidebar.write("- Yasin Tanış")
    
    st.sidebar.title("MIUUL VERIPOTTER")
    
    # Kullanıcı sistemi başlat
    init_user_system()
    
    # Veriyi yükle
    netflix_data, spotify_data, books_data = load_data()
    
    # Yan menü sekmeler
    sidebar_selection = st.sidebar.radio(
        "Menü",
        ["Ana Sayfa", "Ruh Hali Analizi", "Yüz İfadesi Analizi", "Favorilerim", "Geçmiş Kayıtlar", "Podcast ve Videolar", "Hakkında"]
    )
    
    # Kullanıcı girişi veya kaydı
    user_logged_in = login_page()
    
    if sidebar_selection == "Ana Sayfa":
        st.write("## 🏠 Hoş Geldiniz!")
        st.write("""
        MindMingle 2.0, günlük ruh halinizi analiz ederek size özel içerik önerileri sunan gelişmiş bir platformdur. 
        Mental sağlığınızı desteklemek ve kendinize uygun içeriklerle vakit geçirmenizi sağlamak amacıyla tasarlanmıştır.
        
        ### 🆕 Yeni Özellikler:
        - 📷 **Yüz İfadesi Analizi**: Kameranızı kullanarak yüz ifadenize göre ruh halinizi tespit edin
        - 👤 **Kullanıcı Hesapları**: Kişisel hesabınızla önerilerinizi ve geçmişinizi saklayın
        - 🎧 **Spotify Entegrasyonu**: Ruh halinize uygun şarkıları doğrudan dinleyin
        - 🎙️ **Podcast Önerileri**: Mental sağlığınıza faydalı podcast'leri keşfedin
        - 📺 **YouTube Önerileri**: Ruh halinize uygun video içeriklerini izleyin
        
        ### 📊 Nasıl Çalışır?
        1. **Değerlendirme**: Kısa bir değerlendirme veya yüz analizi ile günlük ruh halinizi belirleriz
        2. **Analiz**: Verdiğiniz yanıtları veya yüz ifadenizi analiz ederek mental durumunuzu tespit ederiz
        3. **Kişiselleştirilmiş Öneriler**: Ruh halinize uygun film, müzik, kitap, podcast ve video içeriklerini sunarız
        
        ### 🎯 Neden MindMingle?
        * 🔄 Her gün değişen ruh halinize göre farklı öneriler
        * 📈 Ruh hali değişimlerinizi takip etme imkanı
        * 🎭 Kendinizi daha iyi hissetmeniz için özelleştirilmiş içerikler
        * 💾 Favori içeriklerinizi kaydetme ve tekrar erişebilme
        
        Başlamak için yan menüden "Ruh Hali Analizi" veya "Yüz İfadesi Analizi" sekmesine geçebilirsiniz.
        """)
        
        # Ana sayfada demo göster
        st.write("## 🎬 En Popüler İçerikler")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="card">
                <h3>🎵 Bu Haftanın En Çok Dinlenen Şarkıları</h3>
                <ul>
                    <li>Seven (feat. Latto) - Jung Kook</li>
                    <li>LALA - Myke Towers</li>
                    <li>vampire - Olivia Rodrigo</li>
                    <li>Cruel Summer - Taylor Swift</li>
                    <li>WHERE SHE GOES - Bad Bunny</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="card">
                <h3>🎬 Öne Çıkan Film Önerileri</h3>
                <ul>
                    <li>Inside Out 2 - Animasyon</li>
                    <li>The Shawshank Redemption - Drama</li>
                    <li>Inception - Bilim Kurgu</li>
                    <li>The Grand Budapest Hotel - Komedi</li>
                    <li>Parasite - Gerilim</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="card">
                <h3>📚 Ayın Kitapları</h3>
                <ul>
                    <li>Atomic Habits - James Clear</li>
                    <li>The Midnight Library - Matt Haig</li>
                    <li>Ikigai - Héctor García & Francesc Miralles</li>
                    <li>The Power of Now - Eckhart Tolle</li>
                    <li>Thinking, Fast and Slow - Daniel Kahneman</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    elif sidebar_selection == "Ruh Hali Analizi":
        if not user_logged_in:
            st.warning("Bu özelliği kullanmak için lütfen giriş yapın veya hesap oluşturun.")
        else:
            st.write("## 🔍 Bugün Kendinizi Nasıl Hissediyorsunuz?")
            
            with st.form("mood_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    feeling = st.slider("😊 Mutluluk Seviyeniz (1-10):", min_value=1, max_value=10, value=5, 
                                       help="Ne kadar mutlu hissediyorsunuz?")
                    activity = st.slider("🏃‍♂️ Günlük Aktivite Seviyeniz (1-10):", min_value=1, max_value=10, value=5,
                                        help="Bugün ne kadar aktif oldunuz?")
                
                with col2:
                    energy_level = st.slider("⚡ Enerji Seviyeniz (1-10):", min_value=1, max_value=10, value=5,
                                            help="Enerjinizi nasıl değerlendirirsiniz?")
                    social_interaction = st.slider("👥 Sosyal Etkileşim (1-10):", min_value=1, max_value=10, value=5,
                                                  help="Sosyal etkileşimleriniz nasıldı?")
                
                submitted = st.form_submit_button("Analizi Tamamla ve Önerileri Gör")
            
            if submitted:
                with st.spinner('Analiz yapılıyor...'):
                    time.sleep(1)  # Kullanıcı deneyimi için kısa bir bekleme
                    
                    mood = calculate_mood(feeling, activity, energy_level, social_interaction)
                    
                    # Ruh hali geçmişine ekle
                    if user_logged_in:
                        mood_data = {
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "time": datetime.now().strftime("%H:%M"),
                            "mood": mood,
                            "feeling": feeling,
                            "activity": activity,
                            "energy": energy_level,
                            "social": social_interaction
                        }
                        save_user_mood_history(st.session_state.username, mood_data)
                    
                    # Görsel gösterim için radar chart
                    mood_chart = generate_mood_chart(feeling, activity, energy_level, social_interaction)
                    
                    # Sonuçları göster
                    st.success(f"Analiz tamamlandı! Bugünkü ruh haliniz: **{mood}**")
                    
                    col1, col2 = st.columns([2, 3])
                    
                    with col1:
                        st.plotly_chart(mood_chart, use_container_width=True)
                        
                        if mood == "Çok Mutlu":
                            st.balloons()
                            st.write("Bugün çok mutlusun. Tavsiyelerimizin tadını çıkar!")
                        elif mood == "Mutlu":
                            st.write("Bugün Mutlusun. Hadi biraz daha eğlenelim!")
                        elif mood == "Üzgün":
                            st.write("Bugün biraz üzgünsün. Yalnız değilsin, birlikte film izleyip müzik dinleyebiliriz.")
                        elif mood == "Keyifli":
                            st.write("Bugün oldukça keyiflisin. İçeceğini alabilir ve kendini tavsiyelerimize bırakabilirsin.")
                        elif mood == "Melankolik":
                            st.write("Bugün biraz melankolik takılıyorsun. Hadi gel film başlıyor.")
                    
                    with col2:
                        # Öneriler için sekmeler
                        tab1, tab2, tab3 = st.tabs(["🎬 Film Önerileri", "🎵 Müzik Önerileri", "📚 Kitap Önerileri"])
                        
                        with tab1:
                            filtered_films = filter_netflix_by_mood(netflix_data, mood)
                            if not filtered_films.empty:
                                for index, row in filtered_films.iterrows():
                                    with st.container():
                                        st.markdown(f"""
                                        <div class="card">
                                            <h4>{row['title']}</h4>
                                            <p><b>Tür:</b> {row['listed_in']}</p>
                                            <p>{row['description'][:150]}...</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                        # Favorilere ekle butonu
                                        if st.button(f"❤️ Favorilere Ekle", key=f"fav_movie_{index}"):
                                            content_data = {
                                                "id": str(index),
                                                "title": row['title'],
                                                "type": row['listed_in'],
                                                "description": row['description'][:150],
                                                "added_date": datetime.now().strftime("%Y-%m-%d")
                                            }
                                            success, message = add_to_favorites(st.session_state.username, "movies", content_data)
                                            if success:
                                                st.success(message)
                                            else:
                                                st.info(message)
                            else:
                                st.write("Üzgünüz, bu ruh halinize uygun film bulunamadı.")
                        
                        with tab2:
                            filtered_songs = filter_spotify_by_mood(spotify_data, mood)
                            if not filtered_songs.empty:
                                for index, row in filtered_songs.iterrows():
                                    with st.container():
                                        st.markdown(f"""
                                        <div class="card">
                                            <h4>{row['track_name']}</h4>
                                            <p><b>Sanatçı:</b> {row['artist(s)_name']}</p>
                                            <p><b>Dans Edilebilirlik:</b> {row['danceability_%']}% | <b>Enerji:</b> {row['energy_%']}%</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                        # Favorilere ekle butonu
                                        if st.button(f"❤️ Favorilere Ekle", key=f"fav_music_{index}"):
                                            content_data = {
                                                "id": str(index),
                                                "title": row['track_name'],
                                                "artist": row['artist(s)_name'],
                                                "added_date": datetime.now().strftime("%Y-%m-%d")
                                            }
                                            success, message = add_to_favorites(st.session_state.username, "music", content_data)
                                            if success:
                                                st.success(message)
                                            else:
                                                st.info(message)
                            else:
                                st.write("Üzgünüz, bu ruh halinize uygun şarkı bulunamadı.")
                        
                        with tab3:
                            filtered_books = filter_books_by_mood(books_data, mood)
                            if not filtered_books.empty:
                                for index, row in filtered_books.iterrows():
                                    with st.container():
                                        st.markdown(f"""
                                        <div class="card">
                                            <h4>{row['Book-Title']}</h4>
                                            <p><b>Yazar:</b> {row['Book-Author']}</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                        # Favorilere ekle butonu
                                        if st.button(f"❤️ Favorilere Ekle", key=f"fav_book_{index}"):
                                            content_data = {
                                                "id": str(index),
                                                "title": row['Book-Title'],
                                                "author": row['Book-Author'],
                                                "added_date": datetime.now().strftime("%Y-%m-%d")
                                            }
                                            success, message = add_to_favorites(st.session_state.username, "books", content_data)
                                            if success:
                                                st.success(message)
                                            else:
                                                st.info(message)
                            else:
                                st.write("Üzgünüz, bu ruh halinize uygun kitap bulunamadı.")
                    
                    # Spotify önerileri
                    st.write("## 🔈 Spotify Müzik Önerileri")
                    spotify_recommendations_component(mood, filtered_songs)
                    
                    # Podcast ve YouTube önerileri
                    podcast_youtube_component(mood)
    
    elif sidebar_selection == "Yüz İfadesi Analizi":
        if not user_logged_in:
            st.warning("Bu özelliği kullanmak için lütfen giriş yapın veya hesap oluşturun.")
        else:
            detected_mood = emotion_detector_component()
            
            if detected_mood:
                st.success(f"Yüz ifadenize göre tespit edilen ruh haliniz: **{detected_mood}**")
                
                # Ruh hali geçmişine ekle
                mood_data = {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "time": datetime.now().strftime("%H:%M"),
                    "mood": detected_mood,
                    "method": "face_detection"
                }
                save_user_mood_history(st.session_state.username, mood_data)
                
                # Önerileri göster
                st.write("## 📊 İçerik Önerileri")
                
                tab1, tab2, tab3 = st.tabs(["🎬 Film Önerileri", "🎵 Müzik Önerileri", "📚 Kitap Önerileri"])
                
                with tab1:
                    filtered_films = filter_netflix_by_mood(netflix_data, detected_mood)
                    if not filtered_films.empty:
                        for index, row in filtered_films.iterrows():
                            st.markdown(f"""
                            <div class="card">
                                <h4>{row['title']}</h4>
                                <p><b>Tür:</b> {row['listed_in']}</p>
                                <p>{row['description'][:150]}...</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.write("Üzgünüz, bu ruh halinize uygun film bulunamadı.")
                
                with tab2:
                    filtered_songs = filter_spotify_by_mood(spotify_data, detected_mood)
                    if not filtered_songs.empty:
                        for index, row in filtered_songs.iterrows():
                            st.markdown(f"""
                            <div class="card">
                                <h4>{row['track_name']}</h4>
                                <p><b>Sanatçı:</b> {row['artist(s)_name']}</p>
                                <p><b>Dans Edilebilirlik:</b> {row['danceability_%']}% | <b>Enerji:</b> {row['energy_%']}%</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.write("Üzgünüz, bu ruh halinize uygun şarkı bulunamadı.")
                
                with tab3:
                    filtered_books = filter_books_by_mood(books_data, detected_mood)
                    if not filtered_books.empty:
                        for index, row in filtered_books.iterrows():
                            st.markdown(f"""
                            <div class="card">
                                <h4>{row['Book-Title']}</h4>
                                <p><b>Yazar:</b> {row['Book-Author']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.write("Üzgünüz, bu ruh halinize uygun kitap bulunamadı.")
                
                # Spotify önerileri
                st.write("## 🔈 Spotify Müzik Önerileri")
                spotify_recommendations_component(detected_mood, filtered_songs)
                
                # Podcast ve YouTube önerileri
                podcast_youtube_component(detected_mood)
    
    elif sidebar_selection == "Favorilerim":
        if not user_logged_in:
            st.warning("Favorilerinizi görmek için lütfen giriş yapın veya hesap oluşturun.")
        else:
            st.write("## ❤️ Favori İçerikleriniz")
            
            # Favori içerikleri al
            favorites = get_user_favorites(st.session_state.username)
            
            # Favorileri göster
            tab1, tab2, tab3 = st.tabs(["🎬 Favori Filmler", "🎵 Favori Müzikler", "📚 Favori Kitaplar"])
            
            with tab1:
                st.write("### Favori Filmleriniz")
                if favorites["movies"]:
                    for movie in favorites["movies"]:
                        st.markdown(f"""
                        <div class="card">
                            <h4>{movie['title']}</h4>
                            <p><b>Tür:</b> {movie['type']}</p>
                            <p>{movie['description']}...</p>
                            <p><small>Eklenme Tarihi: {movie['added_date']}</small></p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Henüz favori film eklemediniz.")
            
            with tab2:
                st.write("### Favori Şarkılarınız")
                if favorites["music"]:
                    for music in favorites["music"]:
                        st.markdown(f"""
                        <div class="card">
                            <h4>{music['title']}</h4>
                            <p><b>Sanatçı:</b> {music['artist']}</p>
                            <p><small>Eklenme Tarihi: {music['added_date']}</small></p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Henüz favori şarkı eklemediniz.")
            
            with tab3:
                st.write("### Favori Kitaplarınız")
                if favorites["books"]:
                    for book in favorites["books"]:
                        st.markdown(f"""
                        <div class="card">
                            <h4>{book['title']}</h4>
                            <p><b>Yazar:</b> {book['author']}</p>
                            <p><small>Eklenme Tarihi: {book['added_date']}</small></p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Henüz favori kitap eklemediniz.")
    
    elif sidebar_selection == "Geçmiş Kayıtlar":
        if not user_logged_in:
            st.warning("Geçmiş kayıtlarınızı görmek için lütfen giriş yapın veya hesap oluşturun.")
        else:
            st.write("## 📈 Ruh Hali Geçmişiniz")
            
            # Kullanıcının ruh hali geçmişini al
            mood_history = get_user_mood_history(st.session_state.username)
            
            if mood_history:
                # Verileri düzenle
                dates = [entry["date"] for entry in mood_history]
                moods = [entry["mood"] for entry in mood_history]
                
                # Ruh hallerini sayısal değerlere dönüştür
                mood_values = []
                for mood in moods:
                    if mood == "Çok Mutlu":
                        mood_values.append(5)
                    elif mood == "Mutlu":
                        mood_values.append(4)
                    elif mood == "Keyifli":
                        mood_values.append(3)
                    elif mood == "Melankolik":
                        mood_values.append(2)
                    else:  # Üzgün
                        mood_values.append(1)
                
                # Grafik oluştur
                fig = px.line(
                    x=dates,
                    y=mood_values,
                    labels={'x': 'Tarih', 'y': 'Ruh Hali'},
                    title="Ruh Hali Değişimi"
                )
                
                # Y eksenindeki etiketleri değiştir
                fig.update_layout(
                    yaxis=dict(
                        tickmode='array',
                        tickvals=[1, 2, 3, 4, 5],
                        ticktext=['Üzgün', 'Melankolik', 'Keyifli', 'Mutlu', 'Çok Mutlu']
                    )
                )
                
                st.plotly_chart(fig)
                
                # Geçmiş kayıtları tablo olarak göster
                st.write("### Geçmiş Ruh Hali Kayıtları")
                
                for entry in mood_history:
                    date_time = f"{entry['date']} {entry.get('time', '')}"
                    mood = entry['mood']
                    method = entry.get('method', 'manuel')
                    
                    st.markdown(f"""
                    <div class="card">
                        <h4>{date_time}</h4>
                        <p><b>Ruh Hali:</b> {mood}</p>
                        <p><b>Analiz Metodu:</b> {'Yüz Tanıma' if method == 'face_detection' else 'Manuel Değerlendirme'}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Geçmişi temizle butonu
                if st.button("Geçmişi Temizle"):
                    # Boş bir geçmiş kaydet
                    save_user_mood_history(st.session_state.username, [])
                    st.success("Geçmiş kayıtlar temizlendi!")
                    st.experimental_rerun()
            else:
                st.info("Henüz ruh hali kaydınız bulunmamaktadır.")
    
    elif sidebar_selection == "Podcast ve Videolar":
        if not user_logged_in:
            st.warning("Bu özelliği kullanmak için lütfen giriş yapın veya hesap oluşturun.")
        else:
            st.write("## 🎧 Podcast ve Video Önerileri")
            
            # Mevcut ruh hali seçimi
            mood_options = ["Çok Mutlu", "Mutlu", "Keyifli", "Melankolik", "Üzgün"]
            selected_mood = st.selectbox("Hangi ruh hali için öneriler almak istersiniz?", mood_options)
            
            # Podcast ve YouTube önerileri
            podcast_youtube_component(selected_mood)
    
    elif sidebar_selection == "Hakkında":
        st.write("## 🧠 MindMingle 2.0 Hakkında")
        st.write("""
        MindMingle, kullanıcıların günlük ruh hallerini analiz ederek kişiselleştirilmiş içerik önerileri sunan bir platformdur. 
        
        Mental sağlığı desteklemeyi amaçlayan bu proje, yapay zeka, yüz tanıma ve öneri sistemleri gibi teknolojileri kullanarak kullanıcılara özel film, müzik, kitap, podcast ve video önerileri sunmaktadır.
        
        ### 🌟 Proje Ekibi
        - Yasin Tanış
        - Can Umurhan Öksüz
        - Kadir Alçin
        - Meryem Tarhan Özkul
        - Aycan Karaçanta Kurt
        
        ### 🔍 Kullanılan Teknolojiler
        - Python
        - Streamlit
        - OpenCV ve DeepFace (Yüz İfadesi Tanıma)
        - Spotify API Entegrasyonu
        - YouTube API Entegrasyonu
        - İçerik Filtreleme Algoritmaları
        - Kullanıcı Yönetim Sistemi
        
        ### 📅 Sürüm Geçmişi
        - v1.0: İlk versiyon - Temel ruh hali analizi ve film/müzik önerileri
        - v1.1: Kitap önerisi sistemi eklendi
        - v1.2: Kullanıcı arayüzü iyileştirmeleri ve ruh hali geçmişi takibi
        - v2.0: Yüz ifadesi tanıma, kullanıcı hesapları, Spotify entegrasyonu, podcast ve YouTube önerileri eklendi
        
        ### 💭 Gelecek Planlar
        - Mobil uygulama geliştirme
        - Kişileştirilmiş meditasyon ve egzersiz önerileri
        - Grup önerileri ve sosyal özellikler
        - Yapay zeka destekli terapi asistanı
        
        ### 📢 Geri Bildirim
        Önerileriniz ve geri bildirimleriniz için ekip üyeleriyle iletişime geçebilirsiniz.
        """)

if __name__ == "__main__":
    main()
