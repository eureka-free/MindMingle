import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import joblib
import matplotlib.pyplot as plt
import plotly.express as px
import time

# Veri setlerini yükleme
netflix_data = pd.read_csv('netflix.csv')  # Netflix veri seti
spotify_data = pd.read_csv('spotify.csv', encoding="ISO-8859-1", sep=",")  # Spotify veri seti
books_data = pd.read_csv('books.csv')  # Kitap veri seti - aktifleştirildi

# Spotify özellikleri ve modelleri
spotify_features = spotify_data[
    ['danceability_%', 'energy_%', 'valence_%', 'acousticness_%', 'instrumentalness_%', 'liveness_%', 'speechiness_%']]
scaler = MinMaxScaler()
spotify_normalized_features = scaler.fit_transform(spotify_features)

# Kitap veri setini hazırlama
tfidf_vectorizer_books = TfidfVectorizer(stop_words='english')
# NaN değerleri boş string ile değiştir
books_data['Book-Title'] = books_data['Book-Title'].fillna('')
books_data['Book-Author'] = books_data['Book-Author'].fillna('')
books_data['combined_features'] = books_data['Book-Title'] + " " + books_data['Book-Author']

# TF-IDF vektörleştiriciyi uygula
tfidf_matrix_books = tfidf_vectorizer_books.fit_transform(books_data['combined_features'])

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

def filter_contents(data, mood):
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

def recommend_music(spotify_data, features, mood, num_recommendations=5):
    # Ruh haline göre müzik filtresi
    if mood in ["Çok Mutlu", "Mutlu"]:
        # Yüksek dans edilebilirlik ve pozitif değerler
        mood_mask = (spotify_data['danceability_%'] > 70) & (spotify_data['valence_%'] > 70)
    elif mood == "Üzgün":
        # Düşük enerji, düşük valence - daha sakin ve duygusal müzikler
        mood_mask = (spotify_data['energy_%'] < 50) & (spotify_data['valence_%'] < 50)
    elif mood == "Keyifli":
        # Orta enerji, yüksek akustik - keyifli ve rahatlatıcı müzikler
        mood_mask = (spotify_data['energy_%'].between(50, 70)) & (spotify_data['acousticness_%'] > 50)
    elif mood == "Melankolik":
        # Yüksek akustik, düşük enerji - derin ve düşündürücü müzikler
        mood_mask = (spotify_data['acousticness_%'] > 60) & (spotify_data['energy_%'] < 60)
    
    filtered_indices = spotify_data[mood_mask].index
    
    if len(filtered_indices) >= num_recommendations:
        # Ruh haline uygun şarkılardan rastgele seç
        selected_indices = np.random.choice(filtered_indices, num_recommendations, replace=False)
        return spotify_data.iloc[selected_indices]
    else:
        # Yeterli sayıda şarkı bulunamazsa, benzerlik skorlarını kullan
        index = np.random.randint(0, len(features))
        cosine_similarities = cosine_similarity(features[index:index + 1], features)
        similar_indices = cosine_similarities.argsort().flatten()[-(num_recommendations + 1):-1]
        return spotify_data.iloc[similar_indices]

def recommend_books(mood, tfidf_matrix, books_data, num_recommendations=5):
    # Ruh haline göre kitap türleri belirleme
    if mood in ["Çok Mutlu", "Mutlu"]:
        genres = ["comedy", "humor", "adventure", "fantasy"]
    elif mood == "Üzgün":
        genres = ["self-help", "inspiration", "memoir", "poetry"]
    elif mood == "Keyifli":
        genres = ["romance", "fiction", "young adult", "travel"]
    elif mood == "Melankolik":
        genres = ["philosophy", "classic", "literary fiction", "mystery"]
    
    # Tür terimlerini içeren kitapları filtreleme
    filtered_books = books_data
    for genre in genres:
        filtered_books = filtered_books[
            filtered_books['Book-Title'].str.contains(genre, case=False, na=False) | 
            filtered_books['combined_features'].str.contains(genre, case=False, na=False)
        ]
    
    if len(filtered_books) >= num_recommendations:
        return filtered_books.sample(n=num_recommendations)
    else:
        # Yeterli sayıda kitap bulunamazsa, benzerlik skorlarını kullan
        index = np.random.randint(0, tfidf_matrix.shape[0])
        cosine_similarities = cosine_similarity(tfidf_matrix[index:index + 1], tfidf_matrix)
        similar_indices = cosine_similarities.argsort().flatten()[-(num_recommendations + 1):-1]
        return books_data.iloc[similar_indices]

def generate_mood_chart(feeling, activity, energy_level, social_interaction):
    # Radar chart verileri
    categories = ['Mutluluk', 'Aktivite', 'Enerji', 'Sosyal Etkileşim']
    values = [feeling, activity, energy_level, social_interaction]
    
    # Plotly ile radar chart
    fig = px.line_polar(
        r=values,
        theta=categories,
        line_close=True,
        range_r=[0, 10],
        title="Ruh Hali Analiz Grafiği"
    )
    fig.update_traces(fill='toself')
    return fig

def create_mood_history(mood):
    if 'mood_history' not in st.session_state:
        st.session_state.mood_history = []
    
    # Günün tarihi ve ruh hali kaydı
    today = pd.Timestamp.now().strftime('%Y-%m-%d')
    
    # Mevcut tarihin kaydı var mı kontrol et
    for i, entry in enumerate(st.session_state.mood_history):
        if entry['date'] == today:
            # Mevcut kaydı güncelle
            st.session_state.mood_history[i]['mood'] = mood
            return
    
    # Yeni kayıt ekle
    st.session_state.mood_history.append({'date': today, 'mood': mood})

def show_mood_history():
    if 'mood_history' in st.session_state and st.session_state.mood_history:
        st.subheader("Geçmiş Ruh Hali Kayıtları")
        
        # Verileri düzenle
        dates = [entry['date'] for entry in st.session_state.mood_history]
        moods = [entry['mood'] for entry in st.session_state.mood_history]
        
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
    else:
        st.info("Henüz ruh hali kaydınız bulunmamaktadır.")

# Sayfa yapılandırması
st.set_page_config(page_title="MINDMINGLE", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
        text-align: center;
        margin: 20px;
        color: #4A90E2;
    }
    .subtitle {
        font-size:20px !important;
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
    button {
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
    button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    .tabs {
        margin-top: 20px;
    }
    </style>
    <div class="big-font">🧠 MINDMINGLE 🎵🎬📚</div>
    <div class="subtitle">Ruh Haline Göre Kişiselleştirilmiş Öneri Platformu</div>
    <p>Merhaba! MindMingle, günlük ruh halinizi analiz ederek size özel film, müzik ve kitap önerileri sunan bir platformdur. Aşağıdaki değerlendirmeyi tamamlayarak mental durumunuzu öğrenebilir ve size özel öneriler alabilirsiniz.</p>
    """, unsafe_allow_html=True)

# Yan menü
st.sidebar.image("logo.png", use_column_width=True)
st.sidebar.title("EUREKA")
st.sidebar.text("Aycan Karaçanta Kurt")
st.sidebar.text("Can Umurhan Öksüz")
st.sidebar.text("Kadir Alçin")
st.sidebar.text("Meryem Tarhan Özkul")
st.sidebar.text("Yasin Tanış")

# Yan menü sekmeler
sidebar_selection = st.sidebar.radio(
    "Menü",
    ["Ana Sayfa", "Ruh Hali Analizi", "Geçmiş Kayıtlar", "Hakkında"]
)

if sidebar_selection == "Ana Sayfa":
    st.write("## 🏠 Hoş Geldiniz!")
    st.write("""
    MindMingle, günlük ruh halinizi analiz ederek size özel içerik önerileri sunan bir platformdur. 
    Mental sağlığınızı desteklemek ve kendinize uygun içeriklerle vakit geçirmenizi sağlamak amacıyla tasarlanmıştır.
    
    ### 📊 Nasıl Çalışır?
    1. **Değerlendirme**: Kısa bir değerlendirme ile günlük ruh halinizi belirleriz
    2. **Analiz**: Verdiğiniz yanıtları analiz ederek mental durumunuzu tespit ederiz
    3. **Kişiselleştirilmiş Öneriler**: Ruh halinize uygun film, müzik ve kitap önerileri sunarız
    
    ### 🎯 Neden MindMingle?
    * 🔄 Her gün değişen ruh halinize göre farklı öneriler
    * 📈 Ruh hali değişimlerinizi takip etme imkanı
    * 🎭 Kendinizi daha iyi hissetmeniz için özelleştirilmiş içerikler
    
    Başlamak için yan menüden "Ruh Hali Analizi" sekmesine geçebilirsiniz.
    """)

elif sidebar_selection == "Ruh Hali Analizi":
    with st.form("mood_form"):
        st.write("## 🔍 Bugün Kendinizi Nasıl Hissediyorsunuz?")
        
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
            create_mood_history(mood)
            
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
                    filtered_films = filter_contents(netflix_data, mood)
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
                    recommended_songs = recommend_music(spotify_data, spotify_normalized_features, mood)
                    if not recommended_songs.empty:
                        for index, row in recommended_songs.iterrows():
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
                    recommended_books = recommend_books(mood, tfidf_matrix_books, books_data)
                    if not recommended_books.empty:
                        for index, row in recommended_books.iterrows():
                            st.markdown(f"""
                            <div class="card">
                                <h4>{row['Book-Title']}</h4>
                                <p><b>Yazar:</b> {row['Book-Author']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.write("Üzgünüz, bu ruh halinize uygun kitap bulunamadı.")

elif sidebar_selection == "Geçmiş Kayıtlar":
    st.write("## 📈 Ruh Hali Geçmişi")
    show_mood_history()
    
    if st.button("Geçmişi Temizle"):
        if 'mood_history' in st.session_state:
            st.session_state.mood_history = []
            st.success("Geçmiş kayıtlar temizlendi!")
            st.experimental_rerun()

elif sidebar_selection == "Hakkında":
    st.write("## 🧠 MindMingle Hakkında")
    st.write("""
    MindMingle, kullanıcıların günlük ruh hallerini analiz ederek kişiselleştirilmiş içerik önerileri sunan bir platformdur. 
    
    Mental sağlığı desteklemeyi amaçlayan bu proje, veri bilimi ve yapay zeka teknolojilerini kullanarak kullanıcılara özel film, müzik ve kitap tavsiyeleri sunmaktadır.
    
    ### 🌟 Proje Ekibi
    - Aycan Karaçanta Kurt
    - Can Umurhan Öksüz
    - Kadir Alçin
    - Meryem Tarhan Özkul
    - Yasin Tanış
    
    ### 🔍 Kullanılan Teknolojiler
    - Python
    - Streamlit
    - Makine Öğrenmesi Algoritmaları
    - Veri Analizi Kütüphaneleri
    
    ### 📅 Sürüm Geçmişi
    - v1.0: İlk versiyon - Temel ruh hali analizi ve film/müzik önerileri
    - v1.1: Kitap önerisi sistemi eklendi
    - v1.2: Kullanıcı arayüzü iyileştirmeleri ve ruh hali geçmişi takibi
    
    ### 📢 Geri Bildirim
    Önerileriniz ve geri bildirimleriniz için ekip üyeleriyle iletişime geçebilirsiniz.
    """)

# Miuul başlığı
st.sidebar.title("MIUUL VERIPOTTER")
