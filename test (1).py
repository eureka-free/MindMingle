
from __1lib__ import *

import csv
import os
import streamlit as st


# Örnek veri setleri yükleme, gerçek veri yüklemek için uygun yöntemler kullanılmalı
netflix_data = pd.read_csv('netflix.csv')  # Netflix veri seti
spotify_data = pd.read_csv('spotify.csv',encoding="ISO-8859-1" , sep="," )  # Spotify veri seti




# books_data = pd.read_csv('books.csv')  # Kitap veri seti

# Özellikleri ve modelleri yükleme
spotify_features = spotify_data[
    ['danceability_%', 'energy_%', 'valence_%', 'acousticness_%', 'instrumentalness_%', 'liveness_%', 'speechiness_%']]
scaler = MinMaxScaler()
spotify_normalized_features = scaler.fit_transform(spotify_features)
tfidf_vectorizer_books = TfidfVectorizer()
# # NaN değerleri boş string ile değiştir
# books_data['Book-Title'] = books_data['Book-Title'].fillna('')
# books_data['Book-Author'] = books_data['Book-Author'].fillna('')

# Şimdi TF-IDF vektörleştiriciyi uygulayabiliriz
# tfidf_matrix_books = tfidf_vectorizer_books.fit_transform(books_data['Book-Title'] + " " + books_data['Book-Author'])


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


def recommend_music(spotify_data, features, num_recommendations=5):
    index = np.random.randint(0, len(features))
    cosine_similarities = cosine_similarity(features[index:index + 1], features)
    similar_indices = cosine_similarities.argsort().flatten()[-(num_recommendations + 1):-1]
    return spotify_data.iloc[similar_indices]


# def recommend_books(tfidf_matrix, books_data, num_recommendations=5):
#     index = np.random.randint(0, tfidf_matrix.shape[0])
#     cosine_similarities = cosine_similarity(tfidf_matrix[index:index + 1], tfidf_matrix)
#     similar_indices = cosine_similarities.argsort().flatten()[-(num_recommendations + 1):-1]
#     return books_data.iloc[similar_indices]


st.set_page_config(page_title="MINDMINGLE", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
        text-align: center;
        margin: 20px;
    }
    button {
        background-color: #4CAF50;
        color: white;
        padding: 8px 16px;
        margin: 10px 0;
        border: none;
        cursor: pointer;
        border-radius: 5px;
    }
    button:hover {
        background-color: #45a049;
    }
    </style>
    <div class="big-font">MINDMINGLE</div>
    <p>Merhabalar! Uygulamamızda günlük duygu durumlarınızı analiz edebilmek için belirlemiş olduğumuz  kriterlere  1 ile 10 arasında puanlama yapmanızı bekliyoruz.  Bu adımlar sonucunda günlük mental durumunuzu öğrenebilecek ve uygulamamızdan film ve müzik önerisi alabileceksiniz. Önerilerimizi yenilemek  için tavsiye butonuna tekrar tıklamanız yeterli </p>
    """, unsafe_allow_html=True)


st.sidebar.image(r"C:\Users\alcin\OneDrive\Masaüstü\projeMindMingle\logo.jpg", use_column_width=True)
st.sidebar.title("EUREKA")
# Sidebar metinleri
st.sidebar.text("Aycan Karaçanta Kurt")
st.sidebar.text("Can Umurhan Öksüz")
st.sidebar.text("Kadir Alçin")
st.sidebar.text("Meryem Tarhan Özkul")
st.sidebar.text("Yasin Tanış")

# Geri bildirim formu
st.sidebar.subheader("Geri Bildirim")
feedback = st.sidebar.text_area("Uygulama hakkındaki düşünceleriniz:")
if st.sidebar.button("Gönder"):
    file_exists = os.path.isfile('feedback.csv')
    mode = 'a' if file_exists else 'w'
    with open('feedback.csv', mode, newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Geri Bildirim'])
        writer.writerow([feedback])
    st.sidebar.write("Geri bildiriminiz için teşekkürler!")

# Miuul başlığı
st.sidebar.title("MIUUL VERIPOTTER")

with st.form("mood_form"):
    st.write("Bugün kendinizi nasıl hissediyorsunuz?")
    feeling = st.slider("Mutluluk Seviyeniz (1-10):", min_value=1, max_value=10, value=5)
    activity = st.slider("Günlük Aktivite Seviyeniz (1-10):", min_value=1, max_value=10, value=5)
    energy_level = st.slider("Enerji Seviyeniz (1-10):", min_value=1, max_value=10, value=5)
    social_interaction = st.slider("Sosyal Etkileşim (1-10):", min_value=1, max_value=10, value=5)
    submitted = st.form_submit_button("Günlük Mental Durum Analizi Ve Tavsiye")

    # if submitted:
    #     mood = calculate_mood(feeling, activity, energy_level, social_interaction)
    #     if mood in ["Çok Mutlu", "Mutlu"]:
    #         st.success("Bugün çok mutlusun.\nTavsiyelerimizin tadını çıkar")
    #     elif mood == "Üzgün":
    #         st.warning("Bugün biraz üzgünsün.\nYalnız değilsin, birlikte film izleyip müzik dinleyebiliriz.")
    #     elif mood == "Keyifli":
    #         st.info("Bugün oldukça keyiflisin.\nİçeceğini alabilir ve kendini tavsiyelerimize bırakabilirsin.")
    #     elif mood == "Melankolik":
    #         st.error("Bugün biraz melankolik takılıyorsun.\nHadi gel film başlıyor.")

    if submitted:
        mood = calculate_mood(feeling, activity, energy_level, social_interaction)
        if mood == "Çok Mutlu":
            st.success("Bugün çok mutlusun.\nTavsiyelerimizin tadını çıkar")
        elif mood == "Mutlu":
            st.success("Bugün Mutlusun.\nHadi biraz eğlenelim")
        elif mood == "Üzgün":
            st.warning("Bugün biraz üzgünsün.\nYalnız değilsin, birlikte film izleyip müzik dinleyebiliriz.")
        elif mood == "Keyifli":
            st.info("Bugün oldukça keyiflisin.\nİçeceğini alabilir ve kendini tavsiyelerimize bırakabilirsin.")
        elif mood == "Melankolik":
            st.error("Bugün biraz melankolik takılıyorsun.\nHadi gel film başlıyor.")

        filtered_films = filter_contents(netflix_data, mood)
        recommended_songs = recommend_music(spotify_data, spotify_normalized_features)

        # Önerilen Filmler
        st.subheader("Sizin İçin Önerilen Filmler:")
        if not filtered_films.empty:
            for index, row in filtered_films.iterrows():
                st.write(f"{row['title']} - {row['listed_in']}")
        else:
            st.write("Üzgünüz, bu ruh halinize uygun film bulunamadı.")

        # Önerilen Şarkılar
        st.subheader("Sizin İçin Önerilen Şarkılar:")
        if not recommended_songs.empty:
            for index, row in recommended_songs.iterrows():
                st.write(f"{row['track_name']} - {row['artist(s)_name']}")
        else:
            st.write("Üzgünüz, bu ruh halinize uygun şarkı bulunamadı.")




