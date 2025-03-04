import cv2
import numpy as np
from deepface import DeepFace
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration
import av
import threading
import time

# WebRTC için gerekli yapılandırma
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

# Duygu tanıma için thread-safe değişken
class VideoTransformer(VideoTransformerBase):
    def __init__(self):
        self.emotion_result = None
        self.last_detection_time = time.time()
        self.detection_interval = 1.0  # saniye cinsinden
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.lock = threading.Lock()

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        current_time = time.time()
        
        # Yüz tespiti ve çerçeve çizimi
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Belirli aralıklarla duygu analizi yap (CPU kullanımını azaltmak için)
            if current_time - self.last_detection_time >= self.detection_interval and len(faces) > 0:
                try:
                    # DeepFace ile duygu analizi
                    face_img = img[y:y+h, x:x+w]
                    result = DeepFace.analyze(face_img, actions=['emotion'], enforce_detection=False)
                    
                    with self.lock:
                        self.emotion_result = result[0]["emotion"]
                    
                    self.last_detection_time = current_time
                except Exception as e:
                    print(f"Duygu analizi hatası: {e}")
                    pass
            
            # Eğer bir duygu tespiti yapıldıysa, ekranda göster
            if self.emotion_result:
                emotion_text = max(self.emotion_result.items(), key=lambda x: x[1])[0]
                cv2.putText(img, emotion_text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
        
        return av.VideoFrame.from_ndarray(img, format="bgr24")

    def get_emotion(self):
        with self.lock:
            return self.emotion_result

def map_emotion_to_mood(emotion):
    """
    DeepFace'in tespit ettiği duyguyu uygulamamızın ruh hali kategorilerine eşler
    """
    if emotion is None:
        return None
    
    dominant_emotion = max(emotion.items(), key=lambda x: x[1])[0]
    
    # Duygu-ruh hali eşleştirme
    emotion_mood_map = {
        "happy": "Mutlu",
        "surprise": "Çok Mutlu",
        "neutral": "Keyifli",
        "sad": "Melankolik",
        "fear": "Melankolik",
        "angry": "Üzgün",
        "disgust": "Üzgün"
    }
    
    return emotion_mood_map.get(dominant_emotion, "Keyifli")

def emotion_detector_component():
    """
    Streamlit uygulamasına eklenebilecek duygu tanıma bileşeni
    """
    st.write("## 📷 Yüz İfadesi ile Ruh Hali Analizi")
    st.write("Kameranızı açarak yüz ifadenize göre otomatik ruh hali tespiti yapabilirsiniz.")
    
    ctx = webrtc_streamer(
        key="emotion-detection",
        video_transformer_factory=VideoTransformer,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
    
    if ctx.video_transformer:
        st.write("Yüzünüzü kameraya doğru konumlandırın...")
        
        # Duygu sonuçlarını göstermek için yer açma
        emotion_placeholder = st.empty()
        mood_placeholder = st.empty()
        
        # Gerçek zamanlı duygu takibi
        while ctx.state.playing:
            # Duygusal durumu alma
            emotion = ctx.video_transformer.get_emotion()
            
            if emotion:
                # Duyguları görselleştirme
                emotion_placeholder.write("### Tespit Edilen Duygular:")
                
                # Çubuk grafiği oluşturma
                emotions_df = {
                    "Duygu": list(emotion.keys()),
                    "Skor": list(emotion.values())
                }
                
                # En belirgin duyguyu bulma
                dominant_emotion = max(emotion.items(), key=lambda x: x[1])[0]
                
                # Duygulara göre ruh hali eşleştirme
                mood = map_emotion_to_mood(emotion)
                mood_placeholder.success(f"### Tahmini Ruh Haliniz: {mood}")
                
                # Değerler yüzde olarak gösterme
                for emo, score in emotion.items():
                    bar_length = int(score * 100)
                    formatted_score = f"{score*100:.1f}%"
                    
                    # Belirgin duygu için farklı renk
                    color = "green" if emo == dominant_emotion else "gray"
                    
                    st.write(f"{emo.capitalize()}: {formatted_score}")
                    st.progress(score)
                
                # Analizin fazla sık güncellenmemesi için kısa bekleme
                time.sleep(0.5)
    
    # Tespit edilen ruh halini döndür
    if ctx.video_transformer and ctx.state.playing:
        emotion = ctx.video_transformer.get_emotion()
        if emotion:
            return map_emotion_to_mood(emotion)
    
    return None
