########################################################################################################################
#                                                                                                                      #
#                                   UYARILARI DEKARTE ETME                                                             #
#                                                                                                                      #
########################################################################################################################
import warnings
warnings.filterwarnings("ignore")

# Öneri Sistemleri
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


# Streamlit
import streamlit as st

# Analiz Görselleştirme
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import plotly.express as px
from bokeh.plotting import figure, show

########################################################################################################################
#                                                                                                                      #
#                                   MAKİNE ÖĞRENMESİ KÜTÜPHANELER                                                      #
#                                                                                                                      #
########################################################################################################################
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from lightgbm import LGBMRegressor
from catboost import CatBoostClassifier
from catboost import CatBoostRegressor
from sklearn.model_selection import cross_validate
from sklearn.preprocessing import RobustScaler
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from sklearn.linear_model import Lasso
from sklearn.linear_model import ElasticNet
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error
from sklearn.exceptions import ConvergenceWarning
from xgboost import XGBRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.metrics import accuracy_score, classification_report
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import google.generativeai as genai
import genai
import os
import joblib