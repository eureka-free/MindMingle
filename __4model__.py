########################################################################################################################
#                                                                                                                      #
#                                         MODEL KURMA / GELİŞTİRME                                                     #
#                                                                                                                      #
# - Makine Öğrenimi Algoritmalarının Seçimi (Problem türünü bağlı olarak regresyon, sınıflandırma veya kümeleme doğru  #
# şekilde tanımlama yapılarak geliştirme ve testler gerçekleştirildi.)                                                 #
# - Model Eğitimi ve Doğrulama (Temel olarak kullanılmak üzere söz konusu sorun için bir model seçmiş ve kurulmuştur.) #
# - Hiperparametre Ayarlaması ve Model Optimizasyonu gibi temel model kurma geliştirme aşaması. (Problem için          #
#   bir karşılaştırma modeli seçip kuruldu.)                                                                           #
########################################################################################################################
#                                                                                                                      #
#                                    One-Hot Encoding                                                                  #
########################################################################################################################
from __3verihazırlama_eda__ import *

# Pandas get_dummies fonksiyonunu kullanarak kategorik değişkenleri dönüştürme
data_encoded = pd.get_dummies(df, columns=['Gender', 'Occupation', 'self_employed', 'family_history', 'treatment',
                                             'Days_Indoors', 'Growing_Stress', 'Changes_Habits', 'Mental_Health_History',
                                             'Mood_Swings', 'Coping_Struggles', 'Work_Interest', 'Social_Weakness',
                                             'Stress_Work_Interaction', 'Stress_Response', 'Stress_Employed',
                                             'Social_Coping_Interaction', 'Occupation_Group', 'Indoor_Duration'])

# One-hot encoding sonrası ilk beş satırı göster
data_encoded.head()
data_encoded.shape

########################################################################################################################
#                                                                                                                      #
#                                    Veri Setini Eğitim ve Test Setlerine Ayırma                                       #
#                                                                                                                      #
########################################################################################################################

# Hedef sütunları birleştirerek tek bir hedef sütunu oluşturma
conditions = [
    (data_encoded['Mood_Swings_High'] == 1),
    (data_encoded['Mood_Swings_Low'] == 1),
    (data_encoded['Mood_Swings_Medium'] == 1)
]

# Koşullara göre sınıfların isimlerini belirleme
choices = ['High', 'Low', 'Medium']

# Numpy'nin select fonksiyonu ile koşullara göre seçim yaparak yeni bir hedef sütunu oluşturma
data_encoded['Mood_Swings'] = np.select(conditions, choices)

# Bağımsız değişkenler ve yeni hedef değişken
X = data_encoded.drop(['Mood_Swings_High', 'Mood_Swings_Low', 'Mood_Swings_Medium', 'Mood_Swings'], axis=1)
y = data_encoded['Mood_Swings']

# Veri setini eğitim ve test seti olarak ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)  # %70 eğitim, %30 test

########################################################################################################################
#                                                                                                                      #
#                                    MODEL DEĞERLENDİRME VE PERFORMANS ANALİZİ                                         #
# - Model Seçimi ve Eğitimi                                                                                            #
# - Model Performans Metriklerinin Belirlenmesi,                                                                       #
# - Modelin Test Verisiyle Değerlendirilmesi,                                                                          #
# - Sonuçların Yorumlanması ve İyileştirme Alanlarının Belirlenmesi.                                                   #
#                                                                                                                      #
#  (Problem türüne uygun herhangi bir yöntem kullanarak  modelin/yaklaşımın performansının karşılaştırılması ve model  #
#  karşılaştırmasının seçilen yaklaşımlar hakkında ne gösterdiği açıklandı.)                                           #
########################################################################################################################

# Sınıflandırma modellerini ve isimlerini bir listeye koyuyoruz.
models = [
    ('LR', LogisticRegression(max_iter=1000)),
    ('KNN', KNeighborsClassifier()),
    ('CART', DecisionTreeClassifier()),
    ('RF', RandomForestClassifier()),
    ('SVM', SVC()),
    ('GBM', GradientBoostingClassifier())
]

# Her model için çapraz doğrulama ile performans değerlendirme
model_performance = []

for name, model in models:
    cv_acc_score = cross_val_score(model, X, y, cv=5, scoring="accuracy")
    model_performance.append((name, cv_acc_score.mean(), cv_acc_score.std()))

# En yüksek doğruluk değerine göre sıralama
model_performance.sort(key=lambda x: x[1], reverse=True)

# Performans değerlerini göstermek için değişkeni döndürme
model_performance

# GBM modelini başlatma
gbm_model = GradientBoostingClassifier(random_state=42)

# Modeli eğitme
gbm_model.fit(X_train, y_train)

# Test verileri üzerinde modeli değerlendirme
y_pred_gbm = gbm_model.predict(X_test)
accuracy_gbm = accuracy_score(y_test, y_pred_gbm)
classification_report_gbm = classification_report(y_test, y_pred_gbm)

print(f"Accuracy for GBM: {accuracy_gbm:.4f}")
print(f"Classification Report for GBM:\n{classification_report_gbm}")

########################################################################################################################
#                                                                                                                      #
#                                              MODEL KAYDETME                                                          #
#                                                                                                                      #
########################################################################################################################


# Modeli dosyaya kaydet
joblib.dump(gbm_model, 'mindmingle_gbm_model.pkl')

# Modeli yüklemek için:
# gbm_model = joblib.load('gbm_model.pkl')


