########################################################################################################################
#                                                                                                                      #
#                                         TAVSİYE SİSTEMLERİ                                                           #
#                    KULLANICILAR İÇİN AYNI TEMALI MÜZİK, FİLM VE KİTAP ÖNERİLERİ                                      #
#                                                                                                                      #
########################################################################################################################

########################################################################################################################
#                                                                                                                      #
#                                  SPOTİFY  /  NETFLIX  / AMAZON BOOKS                                                 #
#                                                                                                                      #
########################################################################################################################
from __1lib__ import *
gbm_model = joblib.load('mindmingle_gbm_model.pkl')

# Spotify veri setini yükleme
spotify_data = pd.read_csv('spotify.csv')

# Netflix veri setini yükleme
netflix_data = pd.read_csv('netflix.csv')

# Kitap veri setini yükleme
books_data = pd.read_csv('books.csv')

# Kitap veri setinden gerekli sütunları seçme
books_features = books_data[['Book-Title', 'Book-Author']]

# Netflix veri setinden gerekli sütunları seçme
netflix_features = netflix_data[['title', 'description', 'listed_in']]

# Spotify veri setinden gerekli sütunları seçme
spotify_features = spotify_data[['track_name', 'artist(s)_name', 'danceability_%', 'energy_%', 'valence_%']]

# Her bir veri seti için örnek verileri gösterme
print("Kitap Özellikleri Örnek:")
print(books_features.head())
print("\nNetflix Özellikleri Örnek:")
print(netflix_features.head())
print("\nSpotify Özellikleri Örnek:")
print(spotify_features.head())


########################################################################################################################
#                                     Spotify   için İçerik Tabanlı Öneri Sistemi                                       #
#                                               Kod Implementasyonu                                                    #
#                                                                                                                      #
########################################################################################################################

# Müzikal özellikleri seçme
spotify_features = spotify_data[['danceability_%', 'energy_%', 'valence_%', 'acousticness_%', 'instrumentalness_%', 'liveness_%', 'speechiness_%']]

# Normalleştirici oluşturma ve uygulama
scaler = MinMaxScaler()
spotify_normalized_features = scaler.fit_transform(spotify_features)

# TF-IDF yerine burada özellik normalleştirme kullanıyoruz
tfidf_matrix = spotify_normalized_features

# Bir şarkı seçelim, örneğin index olarak 10'u kullanalım
spotify_index = 10

# Seçilen şarkı için benzerlik skorları hesapla
cosine_similarities = cosine_similarity(tfidf_matrix[spotify_index].reshape(1, -1), tfidf_matrix)

# Benzerlik skorlarına göre diğer şarkıları sırala
similar_tracks = cosine_similarities.argsort().flatten()[-11:-1]

# En benzer 10 şarkıyı göster
recommended_tracks = spotify_data.iloc[similar_tracks]
print(recommended_tracks[['track_name', 'artist(s)_name']])

########################################################################################################################
#                                     Netflix  için İçerik Tabanlı Öneri Sistemi                                       #
#                                               Kod Implementasyonu                                                    #
#                                                                                                                      #
########################################################################################################################

# Metin özelliklerini birleştir
netflix_data['combined_features'] = netflix_data['description'] + " " + netflix_data['listed_in']

# TF-IDF Vektörleştiriciyi oluştur
tfidf_vectorizer = TfidfVectorizer()

# Vektörleştirme işlemi
tfidf_matrix = tfidf_vectorizer.fit_transform(netflix_data['combined_features'])

# Bir film/dizi seçelim, örneğin index olarak 1'i kullanalım
netflix_index = 65

# Seçilen içerik için benzerlik skorları hesapla
cosine_similarities = cosine_similarity(tfidf_matrix[netflix_index], tfidf_matrix)

# Benzerlik skorlarına göre diğer içerikleri sırala
similar_contents = cosine_similarities.argsort().flatten()[-11:-1]

# En benzer 10 içeriği göster
recommended_contents = netflix_data.iloc[similar_contents]
print(recommended_contents[['title', 'description', 'listed_in']])

########################################################################################################################
#                                     Kitaplar için İçerik Tabanlı Öneri Sistemi                                       #
#                                               Kod Implementasyonu                                                    #
#                                                                                                                      #
########################################################################################################################

# Metin özelliklerini birleştir
books_data['combined_features'] = books_data['Book-Title'] + " " + books_data['Book-Author']

# NaN değerleri boş string ile değiştirme
books_data['combined_features'] = books_data['combined_features'].fillna('')

# TF-IDF Vektörleştirici oluşturma
tfidf_vectorizer = TfidfVectorizer()

# Vektörleştirme işlemi
tfidf_matrix = tfidf_vectorizer.fit_transform(books_data['combined_features'])

print("Vektörleştirme işlemi başarılı:", tfidf_matrix.shape)

# Bir kitap seçelim, örneğin index olarak 0'ı kullanalım
book_index = 63

# Seçilen kitap için benzerlik skorları hesapla
cosine_similarities = cosine_similarity(tfidf_matrix[book_index], tfidf_matrix)

# Benzerlik skorlarına göre diğer kitapları sırala
similar_books = cosine_similarities.argsort().flatten()[-11:-1]

# En benzer 10 kitabı göster
recommended_books = books_data.iloc[similar_books]
print(recommended_books[['Book-Title', 'Book-Author']])


########################################################################################################################
#                                                                                                                      #
#                                  Rastgele Örnek Seçimi ve Öneri Üretimi                                              #
#                                                                                                                      #
########################################################################################################################

#Spotify için Rastgele Şarkı Seçimi ve Öneri

# Rastgele bir şarkı seç
random_spotify_index = np.random.randint(0, len(spotify_data))

# Seçilen şarkı için benzerlik skorları hesapla
cosine_similarities = cosine_similarity(tfidf_matrix[random_spotify_index].reshape(1, -1), tfidf_matrix)

# Benzerlik skorlarına göre diğer şarkıları sırala
similar_tracks_indices = cosine_similarities.argsort().flatten()[-11:-1]
# Benzerlik skorlarını sırala ve en yüksek skorlara sahip indeksleri al
# Burada, tüm skorları dikkate alarak sıralama yapıyoruz ve sonuçlar içinde olmayan yüksek indeksleri almamaya dikkat ediyoruz.
similar_tracks_indices = cosine_similarities.flatten().argsort()[::-1]
similar_tracks_indices = similar_tracks_indices[similar_tracks_indices < len(spotify_data)]  # Geçerli indisleri sınırla

# En benzer 10 şarkıyı al (kendisi hariç)
recommended_tracks = spotify_data.iloc[similar_tracks_indices[1:11]]  # İlk indis kendisi olabileceği için atlıyoruz

# Sonuçları göster
print("Rastgele Seçilen Şarkı:", spotify_data.iloc[random_spotify_index]['track_name'])
print("Önerilen Şarkılar:")
print(recommended_tracks[['track_name', 'artist(s)_name']])

# Netflix için Rastgele Film/Dizi Seçimi ve Öneri

# Rastgele bir içerik seç
random_netflix_index = np.random.randint(0, len(netflix_data))

# Seçilen içerik için benzerlik skorları hesapla
cosine_similarities = cosine_similarity(tfidf_matrix[random_netflix_index], tfidf_matrix)

# Benzerlik skorlarına göre diğer içerikleri sırala
similar_contents_indices = cosine_similarities.argsort().flatten()[-11:-1]

# En benzer 10 içeriği göster
recommended_contents = netflix_data.iloc[similar_contents_indices]
print("Rastgele Seçilen Netflix İçeriği:", netflix_data.iloc[random_netflix_index]['title'])
print("Önerilen İçerikler:")
print(recommended_contents[['title', 'listed_in']])

# Kitaplar için Rastgele Kitap Seçimi ve Öneri

# Rastgele bir kitap seç
random_book_index = np.random.randint(0, len(books_data))

# tfidf_matrix'in boyutunu kontrol et
print("TF-IDF Matris Boyutu:", tfidf_matrix.shape)

# Rastgele bir kitap indeksi seçimini güvenli bir şekilde yapmak için:
random_book_index = np.random.randint(0, tfidf_matrix.shape[0])  # 0 ile satır sayısı arasında rastgele bir değer

# Seçilen kitap için benzerlik skorlarını hesapla
cosine_similarities = cosine_similarity(tfidf_matrix[random_book_index:random_book_index+1], tfidf_matrix)

# İndeksleme ve benzerlik hesaplama işlemini tekrar dene
print("Rastgele seçilen kitap indeksi:", random_book_index)

# Benzerlik skorlarına göre diğer kitapları sırala
similar_books_indices = cosine_similarities.argsort().flatten()[-11:-1]

# En benzer 10 kitabı göster
recommended_books = books_data.iloc[similar_books_indices]
print("Rastgele Seçilen Kitap:", books_data.iloc[random_book_index]['Book-Title'])
print("Önerilen Kitaplar:")
print(recommended_books[['Book-Title', 'Book-Author']])



########################################################################################################################
#                                                                                                                      #
#                                         MODEL DAĞITIMI VE UYGULAMA                                                   #
#                                                                                                                      #
# - Uygulamanın Kullanıcılarla Etkileşimi ve Geri Bildirim Toplama -GitHub'a yüklenmesi ve ardından interaktif webapp  #
# uygulamaları aracılığıyla canlıya alındı.                                                                            #
# - Modelin Üretim Ortamına Entegrasyonu - STREAMLİT & HEROKU                                                          #
########################################################################################################################

# Ruh Hali Filtresi Fonksiyonu
def filter_content_by_mood(mood, filtered_books=None, filtered_movies=None, filtered_songs=None):
    # Her bir içerik türü için ruh hali filtresi uygula
    if mood == "Mutlu":
        # Filtreleme ölçütleri belirle
        pass  # Buraya filtreme kodları gelecek
    elif mood == "Üzgün":
        pass
    elif mood == "Sinirli":
        pass
    elif mood == "Rahat":
        pass
    return filtered_books, filtered_movies, filtered_songs

# Öneri Üretme Fonksiyonu
def generate_recommendations(filtered_books, filtered_movies, filtered_songs):
    # İçerik tabanlı öneri algoritmalarını çalıştır
    pass  # Buraya öneri algoritması kodları gelecek

# Modelin Kaydedilmesi

pickle.dump(filter_content_by_mood, open('filter_by_mood.pkl', 'wb'))
pickle.dump(generate_recommendations, open('generate_recommendations.pkl', 'wb'))


# İleri Seviye Uygulama

# Örnek Python kodu için filtreleme işlemi
def filter_contents(data, mood):
    if mood == "Mutlu":
        filtered_data = data[data['listed_in'].str.contains("Comedy")]
    elif mood == "Üzgün":
        filtered_data = data[data['listed_in'].str.contains("Drama")]
    elif mood == "Sinirli":
        filtered_data = data[data['listed_in'].str.contains("Action")]
    elif mood == "Rahat":
        filtered_data = data[data['listed_in'].str.contains("Documentary")]
    return filtered_data


########################################################################################################################
#                                                                                                                      #
#                                         PROJE RAPORU VE SUNUMU                                                       #
#                                                                                                                      #
# - Proje Sürecinin Belgelendirilmesi.                                                                                 #
# - Projenin Sonuçlarının Sunumu ve İletişimi. (Her bir analiz adımı için, bulgularını ve/veya seçilen yaklaşımların   #
#  gerekçeleri adım adım açıklanmıştır.)                                                                               #
########################################################################################################################






















