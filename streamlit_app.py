import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.express as px

# Veri setlerini yükleme
@st.cache_data
def load_data():
    try:
        netflix_data = pd.read_csv('netflix.csv')  # Netflix veri seti
        spotify_data = pd.read_csv('spotify.csv', encoding="ISO-8859-1", sep=",")  # Spotify veri seti
        return netflix_data, spotify_data
    except Exception as e:
        st.error(f"Veri yükleme hatası: {e}")
        # Boş DataFrame'ler döndür
        return pd.DataFrame(), pd.DataFrame()

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
    if data.empty:
        return pd.DataFrame()
        
    try:
        if mood == "Çok Mutlu" or mood == "Mutlu":
            filtered_data = data[data['listed_in'].str.contains("Comedy") | data['listed_in'].str.contains("Animation")]
        elif mood == "Üzgün":
            filtered_data = data[data['listed_in'].str.contains("Drama") | data['listed_in'].str.contains("Romantic") | data['listed_in'].str.contains("Comedy")]
        elif mood == "Keyifli":
            filtered_data = data[data['listed_in'].str.contains("Family") | data['listed_in'].str.contains("Documentary") | data['listed_in'].str.contains("Animation")]
        elif mood == "Melankolik":
            filtered_data = data[
                data['listed_in'].str.contains("Art House") | data['listed_in'].str.contains("Independent") | data['listed_in'].str.contains("Drama")]
        
        # Yeterli veri yoksa boş DataFrame döndür
        if filtered_data.empty:
            return pd.DataFrame()
            
        return filtered_data.sample(n=min(5, len(filtered_data)))
    except Exception as e:
        st.error(f"Film filtreleme hatası: {e}")
        return pd.DataFrame()

def filter_spotify_by_mood(data, mood):
    """Ruh haline göre Spotify müziklerini filtreler"""
    if data.empty:
        return pd.DataFrame()
        
    try:
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
            return data.sample(n=min(5, len(data)))  # Yeterli sonuç bulunamazsa rastgele 5 şarkı döndür
    except Exception as e:
        st.error(f"Müzik filtreleme hatası: {e}")
        return pd.DataFrame()

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
        page_title="MindMingle",
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
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Başlık
    st.markdown('<div class="big-font">🧠 MINDMINGLE 🎵🎬📚</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Ruh Halinize Göre Kişiselleştirilmiş Öneri Platformu</div>', unsafe_allow_html=True)
    
    # Yan panel
    try:
        st.sidebar.image("logo.png", use_column_width=True)
    except:
        st.sidebar.title("MINDMINGLE")
        
    st.sidebar.title("EUREKA")
    st.sidebar.write("Ekip Üyeleri:")
    st.sidebar.write("- Aycan Karaçanta Kurt")
    st.sidebar.write("- Can Umurhan Öksüz")
    st.sidebar.write("- Kadir Alçin")
    st.sidebar.write("- Meryem Tarhan Özkul")
    st.sidebar.write("- Yasin Tanış")
    
    st.sidebar.title("MIUUL VERIPOTTER")
    
    # Veriyi yükle
    netflix_data, spotify_data = load_data()
    
    # Yan menü sekmeler
    sidebar_selection = st.sidebar.radio(
        "Menü",
        ["Ana Sayfa", "Ruh Hali Analizi", "Hakkında"]
    )
    
    if sidebar_selection == "Ana Sayfa":
        st.write("## 🏠 Hoş Geldiniz!")
        st.write("""
        MindMingle, günlük ruh halinizi analiz ederek size özel içerik önerileri sunan bir platformdur. 
        Mental sağlığınızı desteklemek ve kendinize uygun içeriklerle vakit geçirmenizi sağlamak amacıyla tasarlanmıştır.
        
        ### 📊 Nasıl Çalışır?
        1. **Değerlendirme**: Kısa bir değerlendirme ile günlük ruh halinizi belirleriz
        2. **Analiz**: Verdiğiniz yanıtları analiz ederek mental durumunuzu tespit ederiz
        3. **Kişiselleştirilmiş Öneriler**: Ruh halinize uygun film ve müzik önerileri sunarız
        
        ### 🎯 Neden MindMingle?
        * 🔄 Her gün değişen ruh halinize göre farklı öneriler
        * 🎭 Kendinizi daha iyi hissetmeniz için özelleştirilmiş içerikler
        
        Başlamak için yan menüden "Ruh Hali Analizi" sekmesine geçebilirsiniz.
        """)
        
        # Ana sayfada demo göster
        st.write("## 🎬 En Popüler İçerikler")
        
        col1, col2 = st.columns(2)
        
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
    
    elif sidebar_selection == "Ruh Hali Analizi":
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
                    tab1, tab2 = st.tabs(["🎬 Film Önerileri", "🎵 Müzik Önerileri"])
                    
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
                        else:
                            st.write("Üzgünüz, bu ruh halinize uygun şarkı bulunamadı.")
    
    elif sidebar_selection == "Hakkında":
        st.write("## 🧠 MindMingle Hakkında")
        st.write("""
        MindMingle, kullanıcıların günlük ruh hallerini analiz ederek kişiselleştirilmiş içerik önerileri sunan bir platformdur. 
        
        Mental sağlığı desteklemeyi amaçlayan bu proje, veri bilimi teknolojilerini kullanarak kullanıcılara özel film ve müzik önerileri sunmaktadır.
        
        ### 🌟 Proje Ekibi
        - Yasin Tanış
        - Can Umurhan Öksüz
        - Kadir Alçin
        - Meryem Tarhan Özkul
        - Aycan Karaçanta Kurt
        ### 🔍 Kullanılan Teknolojiler
        - Python
        - Streamlit
        - İçerik Filtreleme Algoritmaları
        
        ### 📅 Sürüm Geçmişi
        - v1.0: İlk versiyon - Temel ruh hali analizi ve film/müzik önerileri
        
        ### 📢 Geri Bildirim
        Önerileriniz ve geri bildirimleriniz için ekip üyeleriyle iletişime geçebilirsiniz.
        """)

if __name__ == "__main__":
    main()
