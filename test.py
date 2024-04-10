
#######################################################################################################################
#                                                                                                                     #
#                                                                                                                     #
#                                                                                                                     #
#                                                                                                                     #
#                                                                                                                     #
#                                                                                                                     #
#                                                                                                                     #
#######################################################################################################################




#######################################################################################################################
#                                                                                                                     #
#                                         VERİ DOĞRULAMA / ÖN İŞLEME                                                  #
#                             Gelişmiş Fonksiyonel Keşifçi Veri Analizi (AF-EDA)                                      #
#                                                                                                                     #
# Tüm değişkenleri sağlanan kriterlere göre doğrulamış ve gerektiğinde analize hazır                                  #
# veriler elde etmek için temizleme görevlerini yerine getirme aşaması.                                               #
# - Genel Resim                                                                                                       #
# - Kategorik Değişken Analizi (Analysis of Categorical Variables)                                                    #
# - Sayısal Değişken Analizi (Analysis of Numerical Variables)                                                        #
# - Hedef Değişken Analizi (Analysis of Target Variable)                                                              #
# - Korelasyon Analizi (Analysis of Correlation)                                                                      #
#######################################################################################################################

# - Genel Resim
from library_ import *
from __functions__ import *

pandas_ince_ayar()

df = pd.read_csv('mental_healt.csv')
df.head()
df_ = df.copy()
df_.head()

# - Doğruluk ve yanlılık oluşmaması için sonuçlar yanlış bilgiler sunmaması açısından gerekli 5 sütun drop edildi.
df = df.drop('Timestamp', axis=1)
# df = df.drop('Mood Swing', axis=1)
# df = df.drop('Expert Diagnose', axis=1)
df = df.drop('Country', axis=1)
# df = df.drop('Patient Number', axis=1)

df.dropna(inplace=True)

check_df(df)


# Nümerik ve Kategorik değişken yakalanması
cat_cols, num_but_cat, cat_but_car  = grab_col_names(df)  # num_cols çıkarıldı sayısal sütün olmadığından hata veriyor.

cat_cols
num_but_cat
cat_but_car

# - Kategorik Değişken Analizi
for col in cat_cols:
    cat_summary(df, col)

# - Hedef Değişken Analizi
for col in ["Occupation", "self_employed", "family_history", "treatment", "Days_Indoors", "Growing_Stress", "Changes_Habits", "Mental_Health_History", "Coping_Struggles", "Work_Interest", "Social_Weakness", "mental_health_interview", "care_options"]:
    grouped_df = df.groupby(["Mood_Swings", col]).size().unstack(fill_value=0)
    print(grouped_df)
    print("\n")



# Bağımlı değişkenin incelenmesi
df["Mood_Swings"].hist(bins=100)
plt.show()

# - Korelasyon Analizi ve Korelasyonların gösterilmesi
df_encoded = pd.get_dummies(df[cat_cols])
corr = df_encoded.corr()
corr

# Korelasyonların gösterilmesi
sns.set(rc={'figure.figsize': (12, 12)})
sns.heatmap(corr, cmap="RdBu")
plt.show()

df.head()
df_.head()

#######################################################################################################################
#                                                                                                                     #
#                                         VERİ GÖRSELLEŞTİRME                                                         #
#                                                                                                                     #
# En az tek değişken veya daha fazla değişken içeren  bir görselleştirme oluşturulmuştur.                             #
# (örn. kolerasyon analizi, histogram, çubuk grafik, tek kutu grafiği dağılım grafiği,                                #
# dolu çubuk grafik, çoklu kutu grafikleri)                                                                           #
# Sunulan bulguları destekleyen görselleştirmeler kullanmıştır.                                                       #
#######################################################################################################################


# Kategorik değişkenlerin dağılımı (Bar grafik)
for col in cat_cols:
    plt.figure(figsize=(10, 6))
    sns.countplot(x=col, data=df)
    plt.title(f"{col} Dağılımı")
    plt.xlabel(col)
    plt.ylabel("Frekans")
    plt.xticks(rotation=45)
    plt.show()


# Korelasyon analizi görselleştirmesi (Kategori kesişimlerini gösteren ısı haritası)
cross_tab = pd.crosstab(df[cat_cols[0]], df[cat_cols[1]])
plt.figure(figsize=(10, 6))
sns.heatmap(cross_tab, annot=True, cmap="YlGnBu")
plt.title(f"{cat_cols[0]} ve {cat_cols[1]} İlişkisi")
plt.xlabel(cat_cols[1])
plt.ylabel(cat_cols[0])
plt.show()

# Çapraz analiz görselleştirmesi (örneğin, cinsiyet ve yaş arasındaki ilişki)
plt.figure(figsize=(10, 6))
sns.countplot(x="Gender", hue="Mood_Swings", data=df)
plt.title("Cinsiyet ve Mental Dalgalanma Arasındaki İlişki")
plt.xlabel("Cinsiyet")
plt.ylabel("Frekans")
plt.show()


#######################################################################################################################
#                                                                                                                     #
#                                         ÖZELLİK MÜHENDİSLİĞİ                                                        #
#                                                                                                                     #
#  Yeni değişkenler türetildi. Özellikleri belirlendi ve Önemli noktalar dahilinde değişkenler üzerinden çalışmalar   #
#  gerçekleştirildi.                                                                                                  #
#                                                                                                                     #
# Growing_Stress ve Changes_Habits değişkenlerini kullanarak kişinin stres altında nasıl alışkanlıklarını             #
# değiştirdiğini gösteren bir özellik oluşturabiliriz. Örneğin, eğer bir kişi Growing_Stress altında "Yes" yanıtını   #
# vermişse ve Changes_Habits için de "Yes" veya "Maybe" demişse, bu kişinin stres altında alışkanlıklarını değiştirme #
# eğiliminde olduğunu gösterebilir. Bunu, "Stress_Response" adında yeni bir özellik olarak kodlayalım.                #
# Bu yeni özelliği, kişinin stres altında alışkanlık değişikliğine olan eğilimini "High", "Medium" veya "Low" olarak  #
# sınıflandırarak oluşturalım.                                                                                        #
#                                                                                                                     #
# #Örneğin, bir kişi Growing_Stress için "Yes" ve Changes_Habits için "Yes"veya "Maybe" yanıtını vermişse, bu kişi    #
# için Stress_Response "High" olarak belirleniyor                                                                     #
#######################################################################################################################


# Eksik Değer Analizi
missing_values_table(df)


#Growing_Stress ve Changes_Habits değişkenlerini kullanarak kişinin stres altında
#nasıl alışkanlıklarını değiştirdiğini gösteren bir özellik oluşturabiliriz.

#Örneğin, eğer bir kişi Growing_Stress altında "Yes" yanıtını vermişse ve
# Changes_Habits için de "Yes" veya "Maybe" demişse, bu kişinin stres altında
# alışkanlıklarını değiştirme eğiliminde olduğunu gösterebilir. Bunu,
# "Stress_Response" adında yeni bir özellik olarak kodlayalım. Bu yeni özelliği,
# kişinin stres altında alışkanlık değişikliğine olan eğilimini "High", "Medium" veya
# "Low" olarak sınıflandırarak oluşturalım.

#Örneğin, bir kişi Growing_Stress için "Yes" ve Changes_Habits için "Yes"
# veya "Maybe" yanıtını vermişse, bu kişi için Stress_Response "High" olarak
#belirleniyor
def create_stress_response_feature(row):
    if row['Growing_Stress'] == 'Yes' and row['Changes_Habits'] in ['Yes', 'Maybe']:
        return 'High'
    elif row['Growing_Stress'] == 'Maybe' or row['Changes_Habits'] == 'Maybe':
        return 'Medium'
    else:
        return 'Low'
df['Stress_Response'] = df.apply(create_stress_response_feature, axis=1)

# Stress_Response değişkenin görselleştirmesi
plt.figure(figsize=(8, 6))
sns.countplot(x='Stress_Response', data=df, palette='viridis')
plt.title('Stres Yanıtı Dağılımı')
plt.xlabel('Stres Yanıtı')
plt.ylabel('Sayı')
plt.show()

#Stres ve Serbest Meslek Etkileşimi:
def growing_stress_self_employed_interaction(row):
    if row['Growing_Stress'] == 'Yes' and row['self_employed'] in ['Yes', 'No']:
        return 'H-Stress_L-Mental_Health'
    elif row['Growing_Stress'] == 'No' and row['self_employed'] in ['Yes', 'No']:
        return 'L-Stress_H-Mental_Health'
    else:
        return 'Other'

df['Stress_Employed'] = df.apply(growing_stress_self_employed_interaction, axis=1)

plt.figure(figsize=(8, 6))
sns.countplot(x='Stress_Employed', hue='Mood_Swings', data=df, palette='muted')
plt.title('Stres ve Serbest Meslek Etkileşimi')
plt.xlabel('Stres ve Meslek Etkileşimi')
plt.ylabel('Sayı')
plt.xticks(rotation=45)
plt.legend(title='Mood_Swings')
plt.show()

df["Stress_Employed"].value_counts()
df.head()

#######################################################################################################################
#                                                                                                                     #
#                                         MODEL KURMA / GELİŞTİRME                                                    #
#                                                                                                                     #
# - Makine Öğrenimi Algoritmalarının Seçimi (Problem türünü bağlı olarak regresyon, sınıflandırma veya kümeleme doğru #
# şekilde tanımlama yapılarak geliştirme ve testler gerçekleştirildi.)                                                #
# - Model Eğitimi ve Doğrulama (Temel olarak kullanılmak üzere söz konusu sorun için bir model seçmiş ve kurulmuştur.)#
# - Hiperparametre Ayarlaması ve Model Optimizasyonu gibi temel model kurma geliştirme aşaması. (Problem için         #
#   bir karşılaştırma modeli seçip kuruldu.)                                                                          #
#######################################################################################################################


#######################################################################################################################
#                                                                                                                     #
#                                    MODEL DEĞERLENDİRME VE PERFORMANS ANALİZİ                                        #
#                                                                                                                     #
# - Model Performans Metriklerinin Belirlenmesi,                                                                      #
# - Modelin Test Verisiyle Değerlendirilmesi,                                                                         #
# - Sonuçların Yorumlanması ve İyileştirme Alanlarının Belirlenmesi.                                                  #
#                                                                                                                     #
#  (Problem türüne uygun herhangi bir yöntem kullanarak  modelin/yaklaşımın performansının karşılaştırılması ve model #
#  karşılaştırmasının seçilen yaklaşımlar hakkında ne gösterdiği açıklandı.)                                          #
#######################################################################################################################


#######################################################################################################################
#                                                                                                                     #
#                                         MODEL DAĞITIMI VE UYGULAMA                                                  #
#                                                                                                                     #
# - Modelin Üretim Ortamına Entegrasyonu - STREAMLİT & HEROKU                                                         #
# - Uygulamanın Kullanıcılarla Etkileşimi ve Geri Bildirim Toplama -GitHub'a yüklenmesi ve ardından interaktif webapp #
# uygulamaları aracılığıyla canlıya alındı.                                                                           #
#######################################################################################################################


#######################################################################################################################
#                                                                                                                     #
#                                         PROJE RAPORU VE SUNUMU                                                      #
#                                                                                                                     #
# - Proje Sürecinin Belgelendirilmesi.                                                                                 #
# - Projenin Sonuçlarının Sunumu ve İletişimi. (Her bir analiz adımı için, bulgularını ve/veya seçilen yaklaşımların   #
#  gerekçeleri adım adım açıklanmıştır.)                                                                              #
#######################################################################################################################

