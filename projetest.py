from library_ import *
from __functions__ import *

pandas_ince_ayar()

df = pd.read_csv('combined_dataset.csv3')

df.head()

df.columns

check_df(df)

# 'Timestamp' sütununu silme
df = df.drop('Timestamp', axis=1)
df = df.drop('Mood Swing', axis=1)
cat_cols, num_but_cat, cat_but_car = grab_col_names(df)

# df = df.drop('Patient Number', axis=1)

df["Anorxia"].value_counts()
df["Patient Number"].value_counts()

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
                      'Ignore & Move-On', 'Nervous Break-down', 'Admit Mistakes', 'Overthinking',
                      'Stress_Response', 'Stress_Concentration', 'Psycho_Response_Habits',
                      'FamilyHistory_Treatment', 'Gender_EmotionalDiagnose', 'Occupation_StressLevel',
                      'Country_Belgium', 'Country_Bosnia and Herzegovina', 'Country_Brazil',
                      'Country_Canada', 'Country_Colombia', 'Country_Costa Rica', 'Country_Croatia',
                      'Country_Czech Republic', 'Country_Denmark', 'Country_Finland', 'Country_France',
                      'Country_Georgia', 'Country_Germany', 'Country_Greece', 'Country_India', 'Country_Ireland',
                      'Country_Israel', 'Country_Italy', 'Country_Mexico', 'Country_Moldova', 'Country_Netherlands',
                      'Country_New Zealand', 'Country_Nigeria', 'Country_Philippines', 'Country_Poland', 'Country_Portugal',
                      'Country_Russia', 'Country_Singapore', 'Country_South Africa', 'Country_Sweden', 'Country_Switzerland',
                      'Country_Thailand', 'Country_United Kingdom', 'Country_United States', 'Occupation_Corporate',
                      'Occupation_Housewife', 'Occupation_Others', 'Occupation_Student', 'Days_Indoors_15-30 days',
                      'Days_Indoors_31-60 days', 'Days_Indoors_Go out Every day', 'Days_Indoors_More than 2 months',
                      'Growing_Stress_No', 'Growing_Stress_Yes', 'Changes_Habits_No', 'Changes_Habits_Yes',
                      'Mental_Health_History_No', 'Mental_Health_History_Yes', 'Mood_Swings_Low', 'Mood_Swings_Medium',
                      'Work_Interest_No', 'Work_Interest_Yes', 'Social_Weakness_No', 'Social_Weakness_Yes',
                      'mental_health_interview_No', 'mental_health_interview_Yes', 'care_options_Not sure', 'care_options_Yes',
                      'Sadness_Seldom', 'Sadness_Sometimes', 'Sadness_Usually', 'Euphoric_Seldom', 'Euphoric_Sometimes',
                      'Euphoric_Usually', 'Exhausted_Seldom', 'Exhausted_Sometimes', 'Exhausted_Usually', 'Sleep dissorder_Seldom',
                      'Sleep dissorder_Sometimes', 'Sleep dissorder_Usually', 'Sexual Activity_2 From 10', 'Sexual Activity_3 From 10',
                      'Sexual Activity_4 From 10', 'Sexual Activity_5 From 10', 'Sexual Activity_6 From 10', 'Sexual Activity_7 From 10',
                      'Sexual Activity_8 From 10', 'Sexual Activity_9 From 10']


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

# 'Concentration' ve 'Optimisim' sütunları için dönüşümü uygulama
df = extract_number_from_string(df, 'Concentration')
df = extract_number_from_string(df, 'Optimisim')


df=df.drop("Expert Diagnose", axis=1)

columns = ['Patient Number'] + [col for col in df.columns if col != 'Patient Number']
df = df[columns]
df.head()
check_df(df)
df.dtypes


y = df["Optimisim"]
X = df.drop(["Optimisim", "Patient Number"], axis=1)

X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,random_state=42)

models = [('LR', LinearRegression()),
          ("Ridge", Ridge()),
          ("Lasso", Lasso()),
          ("ElasticNet", ElasticNet()),
          ('KNN', KNeighborsRegressor()),
          ('CART', DecisionTreeRegressor()),
          ('RF', RandomForestRegressor()),
          ('SVR', SVR()),
          ('GBM', GradientBoostingRegressor()),
          ]

for name, regressor in models:
    rmse = np.mean(np.sqrt(-cross_val_score(regressor, X, y, cv=5, scoring="neg_mean_squared_error")))
    mse = np.mean(-cross_val_score(regressor, X, y, cv=5, scoring="neg_mean_squared_error"))
    print(f"RMSE: {round(rmse, 4)}, MSE: {round(mse, 4)} ({name}) ")

models = [
    ("Ridge", Ridge(), {"alpha": [0.1, 1.0, 10.0]}),
    ("RF", RandomForestRegressor(), {"n_estimators": [50, 100, 200], "max_depth": [None, 10, 20]}),
    ("XGBoost", XGBRegressor(objective='reg:squarederror'), {"n_estimators": [50, 100, 200], "max_depth": [3, 5, 7]}),
    ("LightGBM", LGBMRegressor(), {"n_estimators": [50, 100, 200], "max_depth": [3, 5, 7]}),#Lightgbm çok fazla uyarı verdiği için yorum satırına aldık.
    ("CatBoost", CatBoostRegressor(verbose=False), {"n_estimators": [50, 100, 200], "max_depth": [3, 5, 7]}),
    ("SVR", SVR(), {'C': [0.1, 1, 10], 'kernel': ['linear', 'poly', 'rbf']})
]

for name, model, param_grid in models:
    grid_search = GridSearchCV(model, param_grid, scoring='neg_mean_squared_error', cv=5)
    grid_search.fit(X, y)

    best_params = grid_search.best_params_
    best_score = np.sqrt(-grid_search.best_score_)
    print(f"Best Parameters for {name}: {best_params}")
    print(f"Best RMSE: {round(best_score, 4)}")











#####################################################################################################
'''
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


'''