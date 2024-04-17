import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import joblib

# Örnek veri setleri yükleme, gerçek veri yüklemek için uygun yöntemler kullanılmalı
netflix_data = pd.read_csv('netflix.csv')  # Netflix veri seti
spotify_data = pd.read_csv('spotify.csv')  # Spotify veri seti
books_data = pd.read_csv('books.csv')  # Kitap veri seti

# Özellikleri ve modelleri yükleme
spotify_features = spotify_data[
    ['danceability_%', 'energy_%', 'valence_%', 'acousticness_%', 'instrumentalness_%', 'liveness_%', 'speechiness_%']]
scaler = MinMaxScaler()
spotify_normalized_features = scaler.fit_transform(spotify_features)
tfidf_vectorizer_books = TfidfVectorizer()
# NaN değerleri boş string ile değiştir
books_data['Book-Title'] = books_data['Book-Title'].fillna('')
books_data['Book-Author'] = books_data['Book-Author'].fillna('')

# Şimdi TF-IDF vektörleştiriciyi uygulayabiliriz
tfidf_matrix_books = tfidf_vectorizer_books.fit_transform(books_data['Book-Title'] + " " + books_data['Book-Author'])


def calculate_mood(feeling_score, activity_score, energy_level, social_interaction):
    total_score = feeling_score + activity_score + energy_level + social_interaction
    if total_score >= 30:
        return "Çok Mutlu"
    elif 20 <= total_score < 30:
        return "Mutlu"
    elif 15 <= total_score < 20:
        return "Rahat"
    elif 10 <= total_score < 15:
        return "Melankolik"
    else:
        return "Üzgün"


def filter_contents(data, mood):
    if mood == "Çok Mutlu" or mood == "Mutlu":
        filtered_data = data[data['listed_in'].str.contains("Comedy") | data['listed_in'].str.contains("Animation")]
    elif mood == "Üzgün":
        filtered_data = data[data['listed_in'].str.contains("Drama") | data['listed_in'].str.contains("Romantic")]
    elif mood == "Rahat":
        filtered_data = data[data['listed_in'].str.contains("Family") | data['listed_in'].str.contains("Documentary")]
    elif mood == "Melankolik":
        filtered_data = data[
            data['listed_in'].str.contains("Art House") | data['listed_in'].str.contains("Independent")]
    return filtered_data.sample(n=min(5, len(filtered_data)))


def recommend_music(spotify_data, features, num_recommendations=5):
    index = np.random.randint(0, len(features))
    cosine_similarities = cosine_similarity(features[index:index + 1], features)
    similar_indices = cosine_similarities.argsort().flatten()[-(num_recommendations + 1):-1]
    return spotify_data.iloc[similar_indices]


def recommend_books(tfidf_matrix, books_data, num_recommendations=5):
    index = np.random.randint(0, tfidf_matrix.shape[0])
    cosine_similarities = cosine_similarity(tfidf_matrix[index:index + 1], tfidf_matrix)
    similar_indices = cosine_similarities.argsort().flatten()[-(num_recommendations + 1):-1]
    return books_data.iloc[similar_indices]


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
    """, unsafe_allow_html=True)

st.sidebar.image("logo.png", use_column_width=True)
st.sidebar.title("EUREKA")
st.markdown('<div class="big-font">MINDMINGLE</div>', unsafe_allow_html=True)

with st.form("mood_form"):
    st.write("Bugün kendinizi nasıl hissediyorsunuz?")
    feeling = st.slider("Mutluluk Seviyeniz (1-10):", min_value=1, max_value=10, value=5)
    activity = st.slider("Günlük Aktivite Seviyeniz (1-10):", min_value=1, max_value=10, value=5)
    energy_level = st.slider("Enerji Seviyeniz (1-10):", min_value=1, max_value=10, value=5)
    social_interaction = st.slider("Sosyal Etkileşim (1-10):", min_value=1, max_value=10, value=5)
    submitted = st.form_submit_button("Ruh Halimi Değerlendir")

if submitted:
    mood = calculate_mood(feeling, activity, energy_level, social_interaction)
    st.success(f"Tahmin edilen Ruh Haliniz: {mood}")
    filtered_films = filter_contents(netflix_data, mood)
    recommended_songs = recommend_music(spotify_data, spotify_normalized_features)
    recommended_books = recommend_books(tfidf_matrix_books, books_data)

    st.subheader("Sizin İçin Önerilen Filmler:")
    for index, row in filtered_films.iterrows():
        st.write(f"{row['title']} - {row['listed_in']}")

    st.subheader("Sizin İçin Önerilen Şarkılar:")
    for index, row in recommended_songs.iterrows():
        st.write(f"{row['track_name']} - {row['artist(s)_name']}")

    st.subheader("Sizin İçin Önerilen Kitaplar:")
    for index, row in recommended_books.iterrows():
        st.write(f"{row['Book-Title']} - {row['Book-Author']}")

st.sidebar.subheader("Geri Bildirim")
feedback = st.sidebar.text_area("Uygulama hakkındaki düşünceleriniz:")
if st.sidebar.button("Gönder"):
    with open("feedback.txt", "a") as f:
        f.write(f"{feedback}\n")
    st.sidebar.write("Geri bildiriminiz için teşekkürler!")
