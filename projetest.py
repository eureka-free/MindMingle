from library_ import *
from __functions__ import *

pandas_ince_ayar()

df = pd.read_csv('combined_dataset.csv3')
df.columns

df.head()
# 'Timestamp' sütununu silme
df = df.drop('Timestamp', axis=1)
df = df.drop('Mood Swing', axis=1)

#df = df.drop('Patient Number', axis=1)

df["Anorxia"].value_counts()

check_df(df)

cat_cols, num_but_cat, cat_but_car = grab_col_names(df)

# Örnek kullanım:
cat_cols, num_but_cat, cat_but_car = grab_col_names(df, exclude_cols=["Patient Number"])

for col in cat_cols:
    cat_summary(df, col)

df.describe().T


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
df['Stress_Response'] = df.apply(create_stress_response_feature, axis=1)

#Stres ve Konsantrasyon Etkileşimi:

df['Stress_Concentration'] = df.apply(stress_concentration_interaction, axis=1)

#Psikolojik Tepkiler ve Günlük Alışkanlıklar:

df['Psycho_Response_Habits'] = df.apply(psychological_response_habits_interaction, axis=1)


#Aile Geçmişi ve Mevcut Durum Etkileşimi:

df['FamilyHistory_Treatment'] = df.apply(family_history_treatment_interaction, axis=1)

#Cinsiyet ve Duygusal Durum:
def gender_emotional_diagnose_interaction(row):
    return f"{row['Gender']}_{row['Expert Diagnose']}"

df['Gender_EmotionalDiagnose'] = df.apply(gender_emotional_diagnose_interaction, axis=1)

#Meslek ve Stres Seviyesi:

df['Occupation_StressLevel'] = df.apply(occupation_stress_level_interaction, axis=1)




label_encoder_cols = ['Gender', 'self_employed', 'family_history', 'treatment',
                      'Coping_Struggles', 'Suicidal thoughts', 'Anorxia',
                      'Authority Respect', 'Try-Explanation', 'Aggressive Response',
                      'Ignore & Move-On', 'Nervous Break-down', 'Admit Mistakes', 'Overthinking']

def label_encoder(dataframe, label_col):
    labelencoder = LabelEncoder()
    dataframe[label_col] = labelencoder.fit_transform(dataframe[label_col])
    return dataframe

# Sadece belirli sütunlar için LabelEncoder uygulama
for col in label_encoder_cols:
    df = label_encoder(df, col)


one_hot_encoder_cols = ['Country', 'Occupation', 'Days_Indoors', 'Growing_Stress',
                        'Changes_Habits', 'Mental_Health_History', 'Mood_Swings',
                        'Work_Interest', 'Social_Weakness', 'mental_health_interview',
                        'care_options', 'Sadness', 'Euphoric', 'Exhausted',
                        'Sleep dissorder', 'Sexual Activity']



# Sadece belirli sütunlar için One-Hot Encoder uygulama
df = one_hot_encoder(df, one_hot_encoder_cols, drop_first=True)

df.head()


# 'Concentration' ve 'Optimisim' sütunları için dönüşümü uygulama
df = extract_number_from_string(df, 'Concentration')
df = extract_number_from_string(df, 'Optimisim')


df=df.drop("Expert Diagnose", axis=1)

columns = ['Patient Number'] + [col for col in df.columns if col != 'Patient Number']
df = df[columns]
df.head()
df.describe().T



y = df["Optimisim"]
X = df.drop(["Optimisim", "Patient Number"], axis=1)

def base_models(X, y, scoring="roc_auc"):
    print("Base Models....")
    classifiers = [('LR', LogisticRegression()),
                   ('KNN', KNeighborsClassifier()),
                   ("SVC", SVC()),
                   ("CART", DecisionTreeClassifier()),
                   ("RF", RandomForestClassifier()),
                   ('Adaboost', AdaBoostClassifier()),
                   ('GBM', GradientBoostingClassifier()),
                   ('XGBoost', XGBClassifier(use_label_encoder=False, eval_metric='logloss')),
                   ('LightGBM', LGBMClassifier()),
                   # ('CatBoost', CatBoostClassifier(verbose=False))
                   ]

    for name, classifier in classifiers:
        cv_results = cross_validate(classifier, X, y, cv=3, scoring=scoring)
        print(f"{scoring}: {round(cv_results['test_score'].mean(), 4)} ({name}) ")

base_models(X, y, scoring="accuracy")


