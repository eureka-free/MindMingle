import streamlit as st
import pandas as pd
import numpy as np

# Netflix veri setini yükleyin
netflix_data = pd.read_csv('netflix.csv')


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


# Streamlit sayfa yapılandırması
st.set_page_config(page_title="MINDMINGLE", layout="wide", initial_sidebar_state="expanded")

# Sayfa Stillerini Tanımlama
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

# Logo ve başlık
st.sidebar.image(r"C:\Users\alcin\OneDrive\Masaüstü\projeMindMingle\logo.jpg", use_column_width=True)
st.sidebar.title("EUREKA")

# Ana başlık
st.markdown('<div class="big-font">MINDMINGLE</div>', unsafe_allow_html=True)

# Duygu durumu değerlendirme formu
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

    st.subheader("Sizin İçin Önerilen Filmler:")
    for index, row in filtered_films.iterrows():
        st.write(f"{row['title']} - {row['listed_in']}")

# Geri bildirim formu
st.sidebar.subheader("Geri Bildirim")
feedback = st.sidebar.text_area("Uygulama hakkındaki düşünceleriniz:")
if st.sidebar.button("Gönder"):
    st.sidebar.write("Geri bildiriminiz için teşekkürler!")