import streamlit as st
import pandas as pd
import requests
import json
import os
import random

# YouTube API için gerekli bilgiler
YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"  # Kendi API anahtarınızı buraya girin

# Podcast veritabanı dosyası
PODCASTS_DB_FILE = "podcasts.json"

def init_podcasts_db():
    """Podcast veritabanını oluşturur veya mevcut veritabanını yükler"""
    if not os.path.exists(PODCASTS_DB_FILE):
        # Örnek podcast verileri
        podcasts = {
            "Çok Mutlu": [
                {
                    "title": "Pozitif Psikoloji",
                    "author": "Dr. Sevil Akman",
                    "description": "Mutluluk ve kişisel gelişim odaklı podcast",
                    "image_url": "https://example.com/images/positive_psychology.jpg",
                    "link": "https://example.com/podcasts/positive_psychology"
                },
                {
                    "title": "Kahkahalar ve Motivasyon",
                    "author": "Gülşen Yılmaz",
                    "description": "Pozitif düşünce ve motivasyon üzerine eğlenceli sohbetler",
                    "image_url": "https://example.com/images/motivation.jpg",
                    "link": "https://example.com/podcasts/motivation"
                }
            ],
            "Mutlu": [
                {
                    "title": "Başarı Hikayeleri",
                    "author": "Mert Akıncı",
                    "description": "İlham veren gerçek başarı hikayeleri",
                    "image_url": "https://example.com/images/success_stories.jpg",
                    "link": "https://example.com/podcasts/success_stories"
                },
                {
                    "title": "Kişisel Gelişim",
                    "author": "Ayşe Temel",
                    "description": "Kişisel gelişim ve motivasyon teknikleri",
                    "image_url": "https://example.com/images/personal_growth.jpg",
                    "link": "https://example.com/podcasts/personal_growth"
                }
            ],
            "Keyifli": [
                {
                    "title": "Sakin Yaşam",
                    "author": "Eda Soylu",
                    "description": "Minimal yaşam ve farkındalık üzerine sohbetler",
                    "image_url": "https://example.com/images/calm_life.jpg",
                    "link": "https://example.com/podcasts/calm_life"
                },
                {
                    "title": "Doğa ve İnsan",
                    "author": "Kemal Erdem",
                    "description": "Doğa ile uyum içinde yaşamak üzerine ipuçları",
                    "image_url": "https://example.com/images/nature.jpg",
                    "link": "https://example.com/podcasts/nature"
                }
            ],
            "Melankolik": [
                {
                    "title": "Derin Düşünceler",
                    "author": "Canan Bilge",
                    "description": "Felsefe, psikoloji ve yaşam üzerine derin sohbetler",
                    "image_url": "https://example.com/images/deep_thoughts.jpg",
                    "link": "https://example.com/podcasts/deep_thoughts"
                },
                {
                    "title": "Karanlıktan Aydınlığa",
                    "author": "Serkan Yücel",
                    "description": "Zor zamanlardan çıkış yolları üzerine konuşmalar",
                    "image_url": "https://example.com/images/darkness_to_light.jpg",
                    "link": "https://example.com/podcasts/darkness_to_light"
                }
            ],
            "Üzgün": [
                {
                    "title": "İyileşme Süreçleri",
                    "author": "Dr. Fatma Aslı",
                    "description": "Duygusal iyileşme ve dayanıklılık üzerine uzman görüşleri",
                    "image_url": "https://example.com/images/healing.jpg",
                    "link": "https://example.com/podcasts/healing"
                },
                {
                    "title": "Umut Veren Hikayeler",
                    "author": "Ali Kemal",
                    "description": "Zorluklardan başarıyla çıkan insanların ilham veren hikayeleri",
                    "image_url": "https://example.com/images/hopeful_stories.jpg",
                    "link": "https://example.com/podcasts/hopeful_stories"
                }
            ]
        }
        
        # Veritabanını kaydet
        with open(PODCASTS_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(podcasts, f, ensure_ascii=False, indent=4)
        
        return podcasts
    else:
        # Mevcut veritabanını yükle
        with open(PODCASTS_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

def get_podcasts_for_mood(mood):
    """Ruh haline göre podcast önerileri alır"""
    podcasts = init_podcasts_db()
    return podcasts.get(mood, podcasts.get("Keyifli"))  # Varsayılan olarak "Keyifli" kategorisini kullan

def search_youtube_videos(query, max_results=5):
    """YouTube'da belirli bir sorgu için video araması yapar"""
    if not YOUTUBE_API_KEY or YOUTUBE_API_KEY == "YOUR_YOUTUBE_API_KEY":
        # API anahtarı tanımlanmamış, örnek veriler kullan
        return get_sample_youtube_videos(query, max_results)
    
    search_endpoint = "https://www.googleapis.com/youtube/v3/search"
    search_params = {
        "part": "snippet",
        "q": query,
        "key": YOUTUBE_API_KEY,
        "maxResults": max_results,
        "type": "video",
        "videoEmbeddable": "true"
    }
    
    search_response = requests.get(search_endpoint, params=search_params)
    search_results = search_response.json()
    
    videos = []
    if "items" in search_results:
        for item in search_results["items"]:
            video = {
                "id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                "channel": item["snippet"]["channelTitle"],
                "description": item["snippet"]["description"],
                "link": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            }
            videos.append(video)
    
    return videos

def get_sample_youtube_videos(query, max_results=5):
    """YouTube API olmadan örnek video verileri döndürür"""
    sample_videos = [
        {
            "id": "sample_id_1",
            "title": "Meditasyon Teknikleri - Stresle Başa Çıkma",
            "thumbnail": "https://example.com/images/meditation.jpg",
            "channel": "Sağlıklı Yaşam",
            "description": "Bu videoda temel meditasyon tekniklerini ve stresle başa çıkma yöntemlerini öğreneceksiniz.",
            "link": "https://www.youtube.com/watch?v=sample_id_1"
        },
        {
            "id": "sample_id_2",
            "title": "Motivasyon: Başarı İçin İpuçları",
            "thumbnail": "https://example.com/images/motivation_tips.jpg",
            "channel": "Kişisel Gelişim",
            "description": "Başarılı insanların kullandığı motivasyon teknikleri ve ipuçları.",
            "link": "https://www.youtube.com/watch?v=sample_id_2"
        },
        {
            "id": "sample_id_3",
            "title": "Mindfulness Alıştırmaları",
            "thumbnail": "https://example.com/images/mindfulness.jpg",
            "channel": "Psikoloji ve Bilinç",
            "description": "Günlük hayatta uygulayabileceğiniz mindfulness alıştırmaları.",
            "link": "https://www.youtube.com/watch?v=sample_id_3"
        },
        {
            "id": "sample_id_4",
            "title": "Duygusal Zeka Geliştirme",
            "thumbnail": "https://example.com/images/emotional_intelligence.jpg",
            "channel": "Psikoloji Dünyası",
            "description": "Duygusal zeka nedir ve nasıl geliştirilebilir?",
            "link": "https://www.youtube.com/watch?v=sample_id_4"
        },
        {
            "id": "sample_id_5",
            "title": "Pozitif Düşünce Teknikleri",
            "thumbnail": "https://example.com/images/positive_thinking.jpg",
            "channel": "Mutlu Yaşam",
            "description": "Pozitif düşünce ve yaşam kalitesini artırma teknikleri.",
            "link": "https://www.youtube.com/watch?v=sample_id_5"
        }
    ]
    
    # Sorguya göre filtreleme yapabilirsiniz
    # Bu örnekte rastgele seçiyoruz
    random.shuffle(sample_videos)
    return sample_videos[:max_results]

def get_youtube_recommendations_for_mood(mood):
    """Ruh haline göre YouTube video önerileri alır"""
    # Ruh haline göre arama sorguları belirle
    mood_queries = {
        "Çok Mutlu": ["pozitif enerji", "motivasyon videoları", "mutluluk egzersizleri"],
        "Mutlu": ["kişisel gelişim", "başarı hikayeleri", "motivasyon teknikleri"],
        "Keyifli": ["meditasyon", "mindfulness", "doğa sesleri"],
        "Melankolik": ["derin düşünce", "felsefe sohbetleri", "sakin müzik"],
        "Üzgün": ["iyileşme teknikleri", "duygusal destek", "pozitif affirmasyonlar"]
    }
    
    queries = mood_queries.get(mood, ["mindfulness", "meditasyon", "pozitif düşünce"])
    query = random.choice(queries)
    
    return search_youtube_videos(query)

def display_podcast(podcast):
    """Podcast bilgilerini görüntüler"""
    st.markdown(f"""
    <div style="border:1px solid #ddd; border-radius:10px; padding:15px; margin-bottom:15px;">
        <h4>{podcast['title']}</h4>
        <p><strong>Yapımcı:</strong> {podcast['author']}</p>
        <p>{podcast['description']}</p>
        <p><a href="{podcast['link']}" target="_blank">Podcast'i Dinle</a></p>
    </div>
    """, unsafe_allow_html=True)

def display_youtube_video(video):
    """YouTube video bilgilerini görüntüler"""
    st.markdown(f"""
    <div style="border:1px solid #ddd; border-radius:10px; padding:15px; margin-bottom:15px;">
        <img src="{video['thumbnail']}" style="width:100%; border-radius:5px; margin-bottom:10px;">
        <h4>{video['title']}</h4>
        <p><strong>Kanal:</strong> {video['channel']}</p>
        <p>{video['description']}</p>
        <p><a href="{video['link']}" target="_blank">YouTube'da İzle</a></p>
    </div>
    """, unsafe_allow_html=True)

def podcast_youtube_component(mood):
    """Ruh haline göre podcast ve YouTube önerileri bileşeni"""
    st.write("## 🎧 Podcast ve Video Önerileri")
    
    tab1, tab2 = st.tabs(["🎙️ Podcast Önerileri", "📺 YouTube Önerileri"])
    
    with tab1:
        st.write("### Ruh Halinize Uygun Podcast Önerileri")
        podcasts = get_podcasts_for_mood(mood)
        
        if podcasts:
            for podcast in podcasts:
                display_podcast(podcast)
        else:
            st.info("Bu ruh haline uygun podcast önerisi bulunamadı.")
    
    with tab2:
        st.write("### Ruh Halinize Uygun YouTube Videoları")
        videos = get_youtube_recommendations_for_mood(mood)
        
        if videos:
            for video in videos:
                display_youtube_video(video)
        else:
            st.info("Bu ruh haline uygun YouTube videosu bulunamadı.")
