import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.express as px

# Sabit öneri verileri
def get_static_movie_recommendations(mood):
    """Ruh haline göre statik film önerileri döndürür"""
    movie_recommendations = {
        "Çok Mutlu": [
            {"title": "Inside Out", "type": "Animation, Comedy", "description": "Genç bir kızın duygularının kişileştirilmiş hikayeleri."},
            {"title": "La La Land", "type": "Musical, Romance", "description": "Los Angeles'ta geçen müzikal bir aşk hikayesi."},
            {"title": "The Grand Budapest Hotel", "type": "Comedy, Adventure", "description": "Ünlü bir otel müdürü ve lobicinin hikayesi."},
            {"title": "Toy Story", "type": "Animation, Adventure", "description": "Oyuncakların gizli dünyasını keşfedin."},
            {"title": "School of Rock", "type": "Comedy, Music", "description": "Sahte bir öğretmen öğrencilerine rock müziği öğretir."}
        ],
        "Mutlu": [
            {"title": "Forrest Gump", "type": "Drama, Comedy", "description": "Düşük IQ'lu bir adamın olağanüstü yaşam yolculuğu."},
            {"title": "The Intouchables", "type": "Comedy, Drama", "description": "Zengin bir adamla bakıcısı arasındaki beklenmedik dostluk."},
            {"title": "Big Fish", "type": "Adventure, Fantasy", "description": "Bir baba ile oğlu arasındaki geç gelen uzlaşma hikayesi."},
            {"title": "Amélie", "type": "Comedy, Romance", "description": "Hayatları değiştiren bir kadının hikayesi."},
            {"title": "Paddington", "type": "Adventure, Comedy", "description": "Sevimli bir ayının Londra maceraları."}
        ],
        "Keyifli": [
            {"title": "The Secret Life of Walter Mitty", "type": "Adventure, Comedy", "description": "Sıradan bir adamın olağanüstü hayallerle dolu hikayesi."},
            {"title": "Chef", "type": "Comedy, Drama", "description": "Bir şefin kendi yolunu çizme hikayesi."},
            {"title": "About Time", "type": "Drama, Fantasy", "description": "Zamanı kontrol edebilen bir adamın dokunaklı hikayesi."},
            {"title": "Midnight in Paris", "type": "Fantasy, Romance", "description": "Paris'te zamanda yolculuk yapan bir yazarın hikayesi."},
            {"title": "Little Miss Sunshine", "type": "Comedy, Drama", "description": "Disfonksiyonel bir ailenin yol yolculuğu."}
        ],
        "Melankolik": [
            {"title": "Lost in Translation", "type": "Drama, Romance", "description": "Tokyo'da yolları kesişen iki yalnız ruhun hikayesi."},
            {"title": "Eternal Sunshine of the Spotless Mind", "type": "Drama, Romance", "description": "Anılarını sildirmeye çalışan eski sevgililerin hikayesi."},
            {"title": "Her", "type": "Drama, Romance", "description": "Bir adam ve yapay zeka asistanı arasındaki ilişki."},
            {"title": "The Tree of Life", "type": "Drama, Fantasy", "description": "Bir ailenin hayat yolculuğu."},
            {"title": "Melancholia", "type": "Drama, Sci-Fi", "description": "Yaklaşan kıyamet karşısında iki kız kardeşin hikayesi."}
        ],
        "Üzgün": [
            {"title": "The Pursuit of Happyness", "type": "Biography, Drama", "description": "Bir baba ve oğlunun zorluklara karşı mücadelesi."},
            {"title": "Good Will Hunting", "type": "Drama", "description": "Sorunlu bir dahinin terapi yolculuğu."},
            {"title": "The Shawshank Redemption", "type": "Drama", "description": "Umut ve dayanıklılık üzerine bir hapishane hikayesi."},
            {"title": "A Beautiful Mind", "type": "Biography, Drama", "description": "Şizofreni ile mücadele eden bir matematikçinin hayatı."},
            {"title": "Life is Beautiful", "type": "Comedy, Drama, War", "description": "Nazi kampında oğlunu korumaya çalışan bir babanın hikayesi."}
        ]
    }
    return movie_recommendations.get(mood, [])

def get_static_music_recommendations(mood):
    """Ruh haline göre statik müzik önerileri döndürür"""
    music_recommendations = {
        "Çok Mutlu": [
            {"name": "Happy", "artist": "Pharrell Williams", "features": "Dans: 82%, Enerji: 84%, Pozitiflik: 96%"},
            {"name": "Can't Stop the Feeling!", "artist": "Justin Timberlake", "features": "Dans: 72%, Enerji: 67%, Pozitiflik: 93%"},
            {"name": "Uptown Funk", "artist": "Mark Ronson ft. Bruno Mars", "features": "Dans: 86%, Enerji: 91%, Pozitiflik: 85%"},
            {"name": "Walking on Sunshine", "artist": "Katrina & The Waves", "features": "Dans: 71%, Enerji: 83%, Pozitiflik: 94%"},
            {"name": "Good as Hell", "artist": "Lizzo", "features": "Dans: 73%, Enerji: 77%, Pozitiflik: 89%"}
        ],
        "Mutlu": [
            {"name": "Don't Start Now", "artist": "Dua Lipa", "features": "Dans: 77%, Enerji: 73%, Pozitiflik: 77%"},
            {"name": "Blinding Lights", "artist": "The Weeknd", "features": "Dans: 75%, Enerji: 73%, Pozitiflik: 75%"},
            {"name": "Levitating", "artist": "Dua Lipa", "features": "Dans: 80%, Enerji: 71%, Pozitiflik: 73%"},
            {"name": "I Got You (I Feel Good)", "artist": "James Brown", "features": "Dans: 67%, Enerji: 72%, Pozitiflik: 83%"},
            {"name": "Shake It Off", "artist": "Taylor Swift", "features": "Dans: 71%, Enerji: 78%, Pozitiflik: 76%"}
        ],
        "Keyifli": [
            {"name": "Sunday Morning", "artist": "Maroon 5", "features": "Dans: 68%, Enerji: 52%, Pozitiflik: 67%"},
            {"name": "Put Your Records On", "artist": "Corinne Bailey Rae", "features": "Dans: 61%, Enerji: 57%, Pozitiflik: 65%"},
            {"name": "Banana Pancakes", "artist": "Jack Johnson", "features": "Dans: 54%, Enerji: 51%, Pozitiflik: 62%"},
            {"name": "Three Little Birds", "artist": "Bob Marley", "features": "Dans: 59%, Enerji: 52%, Pozitiflik: 68%"},
            {"name": "Billionaire", "artist": "Travie McCoy ft. Bruno Mars", "features": "Dans: 66%, Enerji: 54%, Pozitiflik: 63%"}
        ],
        "Melankolik": [
            {"name": "Skinny Love", "artist": "Bon Iver", "features": "Dans: 42%, Enerji: 36%, Pozitiflik: 41%"},
            {"name": "Gravity", "artist": "John Mayer", "features": "Dans: 45%, Enerji: 38%, Pozitiflik: 42%"},
            {"name": "To Build a Home", "artist": "The Cinematic Orchestra", "features": "Dans: 37%, Enerji: 34%, Pozitiflik: 36%"},
            {"name": "Hallelujah", "artist": "Jeff Buckley", "features": "Dans: 34%, Enerji: 31%, Pozitiflik: 33%"},
            {"name": "The Night We Met", "artist": "Lord Huron", "features": "Dans: 40%, Enerji: 37%, Pozitiflik: 38%"}
        ],
        "Üzgün": [
            {"name": "Someone Like You", "artist": "Adele", "features": "Dans: 33%, Enerji: 30%, Pozitiflik: 28%"},
            {"name": "Fix You", "artist": "Coldplay", "features": "Dans: 36%, Enerji: 29%, Pozitiflik: 25%"},
            {"name": "Hurt", "artist": "Johnny Cash", "features": "Dans: 31%, Enerji: 29%, Pozitiflik: 22%"},
            {"name": "Say Something", "artist": "A Great Big World & Christina Aguilera", "features": "Dans: 30%, Enerji: 27%, Pozitiflik: 21%"},
            {"name": "Nights in White Satin", "artist": "The Moody Blues", "features": "Dans: 29%, Enerji: 28%, Pozitiflik: 25%"}
        ]
    }
    return music_recommendations.get(mood, [])

def get_static_book_recommendations(mood):
    """Ruh haline göre statik kitap önerileri döndürür"""
    book_recommendations = {
        "Çok Mutlu": [
            {"title": "The Happiness Project", "author": "Gretchen Rubin"},
            {"title": "Yes Please", "author": "Amy Poehler"},
            {"title": "Hyperbole and a Half", "author": "Allie Brosh"},
            {"title": "The Hitchhiker's Guide to the Galaxy", "author": "Douglas Adams"},
            {"title": "Good Omens", "author": "Terry Pratchett & Neil Gaiman"}
        ],
        "Mutlu": [
            {"title": "The Alchemist", "author": "Paulo Coelho"},
            {"title": "Eat, Pray, Love", "author": "Elizabeth Gilbert"},
            {"title": "Wild", "author": "Cheryl Strayed"},
            {"title": "The Little Prince", "author": "Antoine de Saint-Exupéry"},
            {"title": "The Art of Happiness", "author": "Dalai Lama & Howard Cutler"}
        ],
        "Keyifli": [
            {"title": "Hygge: The Danish Way to Live Well", "author": "Meik Wiking"},
            {"title": "Big Magic", "author": "Elizabeth Gilbert"},
            {"title": "A Walk in the Woods", "author": "Bill Bryson"},
            {"title": "The Power of Now", "author": "Eckhart Tolle"},
            {"title": "Zen and the Art of Motorcycle Maintenance", "author": "Robert M. Pirsig"}
        ],
        "Melankolik": [
            {"title": "Norwegian Wood", "author": "Haruki Murakami"},
            {"title": "The Bell Jar", "author": "Sylvia Plath"},
            {"title": "The Road", "author": "Cormac McCarthy"},
            {"title": "Never Let Me Go", "author": "Kazuo Ishiguro"},
            {"title": "The Remains of the Day", "author": "Kazuo Ishiguro"}
        ],
        "Üzgün": [
            {"title": "Man's Search for Meaning", "author": "Viktor E. Frankl"},
            {"title": "When Breath Becomes Air", "author": "Paul Kalanithi"},
            {"title": "Option B", "author": "Sheryl Sandberg & Adam Grant"},
            {"title": "The Year of Magical Thinking", "author": "Joan Didion"},
            {"title": "Reasons to Stay Alive", "author": "Matt Haig"}
        ]
    }
    return book_recommendations.get(mood, [])

# Ruh hali analizi fonksiyonu
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
        3. **Kişiselleştirilmiş Öneriler**: Ruh halinize uygun film, müzik ve kitap önerileri sunarız
        
        ### 🎯 Neden MindMingle?
        * 🔄 Her gün değişen ruh halinize göre farklı öneriler
        * 🎭 Kendinizi daha iyi hissetmeniz için özelleştirilmiş içerikler
        
        Başlamak için yan menüden "Ruh Hali Analizi" sekmesine geçebilirsiniz.
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
                    tab1, tab2, tab3 = st.tabs(["🎬 Film Önerileri", "🎵 Müzik Önerileri", "📚 Kitap Önerileri"])
                    
                    with tab1:
                        movie_recommendations = get_static_movie_recommendations(mood)
                        if movie_recommendations:
                            for movie in movie_recommendations:
                                st.markdown(f"""
                                <div class="card">
                                    <h4>{movie['title']}</h4>
                                    <p><b>Tür:</b> {movie['type']}</p>
                                    <p>{movie['description']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.write("Üzgünüz, bu ruh halinize uygun film bulunamadı.")
                    
                    with tab2:
                        music_recommendations = get_static_music_recommendations(mood)
                        if music_recommendations:
                            for music in music_recommendations:
                                st.markdown(f"""
                                <div class="card">
                                    <h4>{music['name']}</h4>
                                    <p><b>Sanatçı:</b> {music['artist']}</p>
                                    <p>{music['features']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.write("Üzgünüz, bu ruh halinize uygun şarkı bulunamadı.")
                            
                    with tab3:
                        book_recommendations = get_static_book_recommendations(mood)
                        if book_recommendations:
                            for book in book_recommendations:
                                st.markdown(f"""
                                <div class="card">
                                    <h4>{book['title']}</h4>
                                    <p><b>Yazar:</b> {book['author']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.write("Üzgünüz, bu ruh halinize uygun kitap bulunamadı.")
    
    elif sidebar_selection == "Hakkında":
        st.write("## 🧠 MindMingle Hakkında")
        st.write("""
        MindMingle, kullanıcıların günlük ruh hallerini analiz ederek kişiselleştirilmiş içerik önerileri sunan bir platformdur. 
        
        Mental sağlığı desteklemeyi amaçlayan bu proje, veri bilimi teknolojilerini kullanarak kullanıcılara özel film, müzik ve kitap önerileri sunmaktadır.
        
        ### 🌟 Proje Ekibi
        - Aycan Karaçanta Kurt
        - Can Umurhan Öksüz
        - Kadir Alçin
        - Meryem Tarhan Özkul
        - Yasin Tanış
        
        ### 🔍 Kullanılan Teknolojiler
        - Python
        - Streamlit
        - İçerik Filtreleme Algoritmaları
        
        ### 📅 Sürüm Geçmişi
        - v1.0: İlk versiyon - Temel ruh hali analizi ve film/müzik önerileri
        - v1.1: Kitap önerisi sistemi eklendi
        
        ### 📢 Geri Bildirim
        Önerileriniz ve geri bildirimleriniz için ekip üyeleriyle iletişime geçebilirsiniz.
        """)

if __name__ == "__main__":
    main()
