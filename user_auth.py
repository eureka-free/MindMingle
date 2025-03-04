import streamlit as st
import hashlib
import pandas as pd
import os
import json
from datetime import datetime

# Kullanıcı veritabanı dosyası
USER_DB_FILE = "users.json"
USER_DATA_DIR = "user_data"

def init_user_system():
    """Kullanıcı sistemi için gerekli dosya ve dizinleri oluşturur"""
    # Kullanıcılar veritabanını oluştur
    if not os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "w") as f:
            json.dump({}, f)
    
    # Kullanıcı verileri için dizin oluştur
    if not os.path.exists(USER_DATA_DIR):
        os.makedirs(USER_DATA_DIR)

def hash_password(password):
    """Şifreyi güvenli bir şekilde hashler"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, email):
    """Yeni kullanıcı kaydeder"""
    # Kullanıcı veritabanını oku
    with open(USER_DB_FILE, "r") as f:
        users = json.load(f)
    
    # Kullanıcı adı zaten var mı kontrol et
    if username in users:
        return False, "Bu kullanıcı adı zaten kullanılıyor."
    
    # Yeni kullanıcı ekle
    users[username] = {
        "password_hash": hash_password(password),
        "email": email,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Veritabanını güncelle
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f)
    
    # Kullanıcı için veri dizini oluştur
    user_dir = os.path.join(USER_DATA_DIR, username)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
        
        # Kullanıcının ruh hali geçmişi dosyasını oluştur
        mood_history_file = os.path.join(user_dir, "mood_history.json")
        with open(mood_history_file, "w") as f:
            json.dump([], f)
        
        # Kullanıcının favori içerikleri dosyasını oluştur
        favorites_file = os.path.join(user_dir, "favorites.json")
        with open(favorites_file, "w") as f:
            json.dump({
                "movies": [],
                "music": [],
                "books": []
            }, f)
    
    return True, "Kayıt başarılı! Giriş yapabilirsiniz."

def authenticate_user(username, password):
    """Kullanıcı giriş bilgilerini doğrular"""
    # Kullanıcı veritabanını oku
    with open(USER_DB_FILE, "r") as f:
        users = json.load(f)
    
    # Kullanıcı adı var mı kontrol et
    if username not in users:
        return False, "Kullanıcı adı bulunamadı."
    
    # Şifre doğru mu kontrol et
    if users[username]["password_hash"] != hash_password(password):
        return False, "Şifre yanlış."
    
    return True, "Giriş başarılı!"

def save_user_mood_history(username, mood_data):
    """Kullanıcının ruh hali geçmişini kaydeder"""
    user_dir = os.path.join(USER_DATA_DIR, username)
    mood_history_file = os.path.join(user_dir, "mood_history.json")
    
    # Mevcut geçmişi oku
    with open(mood_history_file, "r") as f:
        mood_history = json.load(f)
    
    # Yeni veriyi ekle
    mood_history.append(mood_data)
    
    # Güncellenen geçmişi kaydet
    with open(mood_history_file, "w") as f:
        json.dump(mood_history, f)

def get_user_mood_history(username):
    """Kullanıcının ruh hali geçmişini getirir"""
    user_dir = os.path.join(USER_DATA_DIR, username)
    mood_history_file = os.path.join(user_dir, "mood_history.json")
    
    # Geçmişi oku
    with open(mood_history_file, "r") as f:
        mood_history = json.load(f)
    
    return mood_history

def add_to_favorites(username, content_type, content_data):
    """Kullanıcının favori içeriklerine yeni öğe ekler"""
    user_dir = os.path.join(USER_DATA_DIR, username)
    favorites_file = os.path.join(user_dir, "favorites.json")
    
    # Mevcut favorileri oku
    with open(favorites_file, "r") as f:
        favorites = json.load(f)
    
    # İçerik zaten favorilerde mi kontrol et
    existing_items = favorites[content_type]
    for item in existing_items:
        if item["id"] == content_data["id"]:
            return False, "Bu içerik zaten favorilerinizde."
    
    # Yeni içeriği ekle
    favorites[content_type].append(content_data)
    
    # Güncellenen favorileri kaydet
    with open(favorites_file, "w") as f:
        json.dump(favorites, f)
    
    return True, "İçerik favorilere eklendi!"

def get_user_favorites(username, content_type=None):
    """Kullanıcının favori içeriklerini getirir"""
    user_dir = os.path.join(USER_DATA_DIR, username)
    favorites_file = os.path.join(user_dir, "favorites.json")
    
    # Favorileri oku
    with open(favorites_file, "r") as f:
        favorites = json.load(f)
    
    if content_type:
        return favorites[content_type]
    else:
        return favorites

def login_page():
    """Kullanıcı giriş/kayıt sayfası"""
    # Oturum durumunu kontrol et
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
    
    if st.session_state.logged_in:
        # Kullanıcı zaten giriş yapmış
        st.success(f"Hoş geldiniz, {st.session_state.username}!")
        if st.button("Çıkış Yap"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.experimental_rerun()
        return True
    
    # Giriş/Kayıt sekmelerini oluştur
    tab1, tab2 = st.tabs(["Giriş", "Kayıt Ol"])
    
    with tab1:
        st.write("### 👤 Giriş Yap")
        
        login_username = st.text_input("Kullanıcı Adı", key="login_username")
        login_password = st.text_input("Şifre", type="password", key="login_password")
        
        if st.button("Giriş Yap", key="login_button"):
            if login_username and login_password:
                success, message = authenticate_user(login_username, login_password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    st.success(message)
                    st.experimental_rerun()
                else:
                    st.error(message)
            else:
                st.warning("Lütfen kullanıcı adı ve şifre girin.")
    
    with tab2:
        st.write("### 📝 Yeni Hesap Oluştur")
        
        reg_username = st.text_input("Kullanıcı Adı", key="reg_username")
        reg_email = st.text_input("E-posta", key="reg_email")
        reg_password = st.text_input("Şifre", type="password", key="reg_password")
        reg_password_confirm = st.text_input("Şifre (Tekrar)", type="password", key="reg_password_confirm")
        
        if st.button("Kayıt Ol", key="register_button"):
            if reg_username and reg_email and reg_password:
                if reg_password != reg_password_confirm:
                    st.error("Şifreler eşleşmiyor.")
                else:
                    success, message = register_user(reg_username, reg_password, reg_email)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
            else:
                st.warning("Lütfen tüm alanları doldurun.")
    
    return False
