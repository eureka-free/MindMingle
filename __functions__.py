import warnings

import pandas as pd


def pandas_ince_ayar():
    pd.set_option('display.max_columns', None)
    pd.set_option("display.max_rows", None)
    pd.set_option('display.width', 500)
    pd.set_option('display.expand_frame_repr', False)
    pd.set_option('display.float_format', lambda x: "%.1f" % x)
    warnings.simplefilter(action='ignore', category=Warning)


# Fonksiyonu çağırarak ayarları belirleyebilirsiniz
#pandas_ince_ayar()


def check_df(dataframe, head=5):
    print("##################### Shape #####################")
    print(dataframe.shape)
    print("##################### Types #####################")
    print(dataframe.dtypes)
    print("##################### Head #####################")
    print(dataframe.head(head))
    print("##################### Tail #####################")
    print(dataframe.tail(head))
    print("##################### NA #####################")
    print(dataframe.isnull().sum())
    print("##################### Quantiles #####################")
    print(dataframe.describe([0, 0.05, 0.50, 0.95, 0.99, 1]).T)
    print("##################### Nunique #####################")
    print(dataframe.nunique())


def num_summary(dataframe, numerical_col, plot=False):
    quantiles = [0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 0.99]
    print(dataframe[numerical_col].describe(quantiles).T)

    if plot:
        dataframe[numerical_col].hist()
        plt.xlabel(numerical_col)
        plt.title(numerical_col)
        plt.show(block=True)


def standart_scaler(col_name):
    return (col_name - col_name.mean()) / col_name.std()


def target_summary_with_cat(dataframe, target, categorical_col):
    print(pd.DataFrame({"TARGET_MEAN": dataframe.groupby(categorical_col)[target].mean()}), end="\n\n\n")


def high_correlated_cols(dataframe, plot=False, corr_th=0.90):
    corr = dataframe.corr()
    cor_matrix = corr.abs()
    upper_triangle_matrix = cor_matrix.where(np.triu(np.ones(cor_matrix.shape), k=1).astype(bool))
    drop_list = [col for col in upper_triangle_matrix.columns if any(upper_triangle_matrix[col] > corr_th)]
    if plot:
        import seaborn as sns
        import matplotlib.pyplot as plt
        sns.set(rc={'figure.figsize': (15, 15)})
        sns.heatmap(corr, cmap="RdBu")
        plt.show()
    return drop_list


'''
high_correlated_cols(df)
drop_list = high_correlated_cols(df, plot=True)
df.drop(drop_list, axis=1)
high_correlated_cols(df.drop(drop_list, axis=1), plot=True)
'''


def missing_values_table(dataframe, na_name=True):
    na_columns = [col for col in dataframe.columns if dataframe[col].isnull().sum() > 0]

    n_miss = dataframe[na_columns].isnull().sum().sort_values(ascending=False)

    ratio = (dataframe[na_columns].isnull().sum() / dataframe.shape[0] * 100).sort_values(ascending=False)

    missing_df = pd.concat([n_miss, np.round(ratio, 2)], axis=1, keys=['n_miss', 'ratio'])

    print(missing_df, end="\n")

    if na_name:
        return na_columns


def create_rfm(dataframe):
    # Veriyi Hazırlma
    dataframe["order_num_total"] = (dataframe["order_num_total_ever_online"]
                                    + dataframe["order_num_total_ever_offline"])
    dataframe["customer_value_total"] = (dataframe["customer_value_total_ever_offline"]
                                         + dataframe["customer_value_total_ever_online"])
    date_columns = dataframe.columns[dataframe.columns.str.contains("date")]
    dataframe[date_columns] = dataframe[date_columns].apply(pd.to_datetime)

    # RFM METRIKLERININ HESAPLANMASI
    dataframe["last_order_date"].max()  # 2021-05-30
    analysis_date = dt.datetime(2021, 6, 1)
    rfm = pd.DataFrame()
    rfm["customer_id"] = dataframe["master_id"]
    rfm["recency"] = (analysis_date - dataframe["last_order_date"]).astype('timedelta64[D]')
    rfm["frequency"] = dataframe["order_num_total"]
    rfm["monetary"] = dataframe["customer_value_total"]

    # RF ve RFM SKORLARININ HESAPLANMASI
    rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])
    rfm["RF_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))
    rfm["RFM_SCORE"] = (
                rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str) + rfm['monetary_score'].astype(
            str))

    # SEGMENTLERIN ISIMLENDIRILMESI
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_Risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }
    rfm['segment'] = rfm['RF_SCORE'].replace(seg_map, regex=True)

    return rfm[["customer_id", "recency", "frequency", "monetary", "RF_SCORE", "RFM_SCORE", "segment"]]


def outlier_thresholds(dataframe, col_name, q1=0.25, q3=0.75):
    """
    Bir dataframe için verilen ilgili kolondaki aykırı değerleri tespit edebilmek adına üst ve alt limitleri belirlemeyi
    sağlayan fonksiyondur

    Parameters
    ----------
    dataframe: "Dataframe"i ifade eder.
    col_name: Değişkeni ifade eder.
    q1: Veri setinde yer alan birinci çeyreği ifade eder.
    q3: Veri setinde yer alan üçüncü çeyreği ifade eder.

    Returns
    -------
    low_limit, ve up_limit değerlerini return eder
    Notes
    -------
    low, up = outlier_tresholds(df, col_name) şeklinde kullanılır.
    q1 ve q3 ifadeleri yoru açıktır. Aykırı değerle 0.01 ve 0.99 değerleriyle de tespit edilebilir.

    """
    quartile1 = dataframe[col_name].quantile(q1)
    quartile3 = dataframe[col_name].quantile(q3)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    return low_limit, up_limit


def create_cltv_df(dataframe):
    # Veriyi Hazırlama
    columns = ["order_num_total_ever_online", "order_num_total_ever_offline", "customer_value_total_ever_offline",
               "customer_value_total_ever_online"]
    for col in columns:
        replace_with_thresholds(dataframe, col)

    dataframe["order_num_total"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    dataframe["customer_value_total"] = dataframe["customer_value_total_ever_offline"] + dataframe[
        "customer_value_total_ever_online"]
    dataframe = dataframe[~(dataframe["customer_value_total"] == 0) | (dataframe["order_num_total"] == 0)]
    date_columns = dataframe.columns[dataframe.columns.str.contains("date")]
    dataframe[date_columns] = dataframe[date_columns].apply(pd.to_datetime)

    # CLTV veri yapısının oluşturulması
    dataframe["last_order_date"].max()  # 2021-05-30
    analysis_date = dt.datetime(2021, 6, 1)
    cltv_df = pd.DataFrame()
    cltv_df["customer_id"] = dataframe["master_id"]
    cltv_df["recency_cltv_weekly"] = ((dataframe["last_order_date"] - dataframe["first_order_date"]).astype(
        'timedelta64[D]')) / 7
    cltv_df["T_weekly"] = ((analysis_date - dataframe["first_order_date"]).astype('timedelta64[D]')) / 7
    cltv_df["frequency"] = dataframe["order_num_total"]
    cltv_df["monetary_cltv_avg"] = dataframe["customer_value_total"] / dataframe["order_num_total"]
    cltv_df = cltv_df[(cltv_df['frequency'] > 1)]

    # BG-NBD Modelinin Kurulması
    bgf = BetaGeoFitter(penalizer_coef=0.001)
    bgf.fit(cltv_df['frequency'],
            cltv_df['recency_cltv_weekly'],
            cltv_df['T_weekly'])
    cltv_df["exp_sales_3_month"] = bgf.predict(4 * 3,
                                               cltv_df['frequency'],
                                               cltv_df['recency_cltv_weekly'],
                                               cltv_df['T_weekly'])
    cltv_df["exp_sales_6_month"] = bgf.predict(4 * 6,
                                               cltv_df['frequency'],
                                               cltv_df['recency_cltv_weekly'],
                                               cltv_df['T_weekly'])

    # # Gamma-Gamma Modelinin Kurulması
    ggf = GammaGammaFitter(penalizer_coef=0.01)
    ggf.fit(cltv_df['frequency'], cltv_df['monetary_cltv_avg'])
    cltv_df["exp_average_value"] = ggf.conditional_expected_average_profit(cltv_df['frequency'],
                                                                           cltv_df['monetary_cltv_avg'])

    # Cltv tahmini
    cltv = ggf.customer_lifetime_value(bgf,
                                       cltv_df['frequency'],
                                       cltv_df['recency_cltv_weekly'],
                                       cltv_df['T_weekly'],
                                       cltv_df['monetary_cltv_avg'],
                                       time=6,
                                       freq="W",
                                       discount_rate=0.01)
    cltv_df["cltv"] = cltv

    # CLTV segmentleme
    cltv_df["cltv_segment"] = pd.qcut(cltv_df["cltv"], 4, labels=["D", "C", "B", "A"])

    return cltv_df


def time_based_weighted_average(dataframe, w1=30, w2=28, w3=26, w4=16):
    return dataframe.loc[df["recency_cut"] == "q1", "overall"].mean() * w1 / 100 + \
        dataframe.loc[df["recency_cut"] == "q2", "overall"].mean() * w2 / 100 + \
        dataframe.loc[df["recency_cut"] == "q3", "overall"].mean() * w3 / 100 + \
        dataframe.loc[df["recency_cut"] == "q4", "overall"].mean() * w4 / 100


#time_based_weighted_average(df)

def check_outlier(dataframe, col_name):
    """
    Bir dataframein verilen değişkininde aykırı gözlerimerin bulunup bulunmadığını tespit etmeye yardımcı olan
    fonksiyondur.
    """
    low_limit, up_limit = outlier_thresholds(dataframe, col_name)
    if dataframe[(dataframe[col_name] > up_limit) | (dataframe[col_name] < low_limit)].any(axis=None):
        return True
    else:
        return False


def grab_col_names(dataframe, cat_th=10, car_th=20):
    """

    Veri setindeki kategorik, numerik ve kategorik fakat kardinal değişkenlerin isimlerini verir.
    Not: Kategorik değişkenlerin içerisine numerik görünümlü kategorik değişkenler de dahildir.

    Parameters
    ------
        dataframe: dataframe
                Değişken isimleri alınmak istenilen dataframe
        cat_th: int, optional
                numerik fakat kategorik olan değişkenler için sınıf eşik değeri
        car_th: int, optinal
                kategorik fakat kardinal değişkenler için sınıf eşik değeri

    Returns
    ------
        cat_cols: list
                Kategorik değişken listesi
        num_cols: list
                Numerik değişken listesi
        cat_but_car: list
                Kategorik görünümlü kardinal değişken listesi

    Examples
    ------
        import seaborn as sns
        df = sns.load_dataset("iris")
        print(grab_col_names(df))


    Notes
    ------
        cat_cols + num_cols + cat_but_car = toplam değişken sayısı
        num_but_cat cat_cols'un içerisinde.
        Return olan 3 liste toplamı toplam değişken sayısına eşittir: cat_cols + num_cols + cat_but_car = değişken sayısı

    """

    # cat_cols, cat_but_car
    cat_cols = [col for col in dataframe.columns if dataframe[col].dtypes == "O"]
    num_but_cat = [col for col in dataframe.columns if dataframe[col].nunique() < cat_th and
                   dataframe[col].dtypes != "O"]
    cat_but_car = [col for col in dataframe.columns if dataframe[col].nunique() > car_th and
                   dataframe[col].dtypes == "O"]
    cat_cols = cat_cols + num_but_cat
    cat_cols = [col for col in cat_cols if col not in cat_but_car]

    # num_cols
    num_cols = [col for col in dataframe.columns if dataframe[col].dtypes != "O"]
    num_cols = [col for col in num_cols if col not in num_but_cat]

    print(f"Observations: {dataframe.shape[0]}")
    print(f"Variables: {dataframe.shape[1]}")
    print(f'cat_cols: {len(cat_cols)}')
    print(f'num_cols: {len(num_cols)}')
    print(f'cat_but_car: {len(cat_but_car)}')
    print(f'num_but_cat: {len(num_but_cat)}')
    return cat_cols, num_cols, cat_but_car


def grab_col_names(dataframe, cat_th=10, car_th=20, exclude_cols=None):
    if exclude_cols is None:
        exclude_cols = []

    cat_cols = [col for col in dataframe.columns if dataframe[col].dtypes == "O" and col not in exclude_cols]
    num_but_cat = [col for col in dataframe.columns if
                   dataframe[col].nunique() < cat_th and dataframe[col].dtypes != "O"]
    cat_but_car = [col for col in dataframe.columns if
                   dataframe[col].nunique() > car_th and dataframe[col].dtypes == "O"]

    return cat_cols, num_but_cat, cat_but_car


def grab_outliers(dataframe, col_name, index=False):
    """
    Fonksiyon, verilen dataframe için verilen değişkende yer alan aykırı değerleri getirir. Bun fonksiyon
    "outlier_thresholds" fonksiyonunu içinde barındırdığı için bu fonksiyona bağımlılığı vardır. outlier_tresholds
    fonksiyonu tanımlanmadan kullanılamaz.

    Parameters
    ----------
    dataframe: Aykırı gözlemlerinin yakalanması istenen dataframei ifade eder.
    col_name: İlgili dataframedeki yakalanması istenen dataframede yer alan değişkeni ifade eder.
    index: Yaklanan aykırı gözlemlerin indexini ifade eder

    Returns
    -------
    Şayet "index" değeri true girilmişse yaklanan aykırı gözlemlerin indexlerini return eder

    """

    low, up = outlier_thresholds(dataframe, col_name, index=False)

    if dataframe[((dataframe[col_name] < low) | (dataframe[col_name] > up))].shape[0] > 10:
        print(dataframe[((dataframe[col_name] < low) | (dataframe[col_name] > up))].head())
    else:
        print(dataframe[((dataframe[col_name] < low) | (dataframe[col_name] > up))])

    if index:
        outlier_index = dataframe[((dataframe[col_name] < low) | (dataframe[col_name] > up))].index
        return outlier_index


def grab_col_names(df, cat_th=10, car_th=20):
    cat_cols = [col for col in df.columns if df[col].dtypes == "object"]
    num_but_cat = [col for col in df.columns if df[col].nunique() < cat_th and df[col].dtypes != "object"]
    cat_but_car = [col for col in df.columns if df[col].nunique() > car_th and df[col].dtypes != "object"]
    return cat_cols, num_but_cat, cat_but_car


def remove_outlier(dataframe, col_name):
    """
    Bu fonksiyon kullanıcıya belirlenen üst ve alt limitlere göre aykırı değerlerden ayıklanmış bir dataframe verir
    Fonksiyonun "outlier_thresholds" fonksiyonuna bağımlılığı vardır
    Parameters
    ----------
    dataframe: Verilen dataframei ifade eder
    col_name: Dataframe'e ait değişkeni ifade eder

    Returns
    -------
    Aykırı değerlerden ayıklanmış yeni bir dataframe return eder
    """
    low_limit, up_limit = outlier_thresholds(dataframe, col_name)
    df_without_outliers = dataframe[~((dataframe[col_name] < low_limit) | (dataframe[col_name] > up_limit))]
    return df_without_outliers


def replace_with_thresholds(dataframe, variable):
    """
    Up limitin üzerinde yer alan değerleri up değeri ile low limitin altında yer alan değerli ise low değerliyle
    baskılar. Bu fonksiyonun da "outlier_thresholds" fonksiyonuna bağımlılığı vardır.
    Parameters
    ----------
    dataframe: Aykırı değerli bakılanmak istenen dataframei ifade eder.
    variable: Bir başka deyişle col_name'i ifade eder. Aykırı değerleri baskılanacak olan dataframe'in ilgili
    değişkenidir.

    Returns
    -------
    Herhangi bir değer return etmez
    """
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit


def missing_values_table(dataframe, na_name=False):
    """

    Bir veri setindeki eksik gözlemleri tespit etmek için kullanılan fonksiyondur. Fonksiyon kullanıcıya "n_miss" ile
    eksik gözlem sayısını "ratio" ile de eksik gözlemlerin değişkende kapladığı yeri yüzdelik olarak ifade eder

    Parameters
    ----------
    dataframe: Veri setini ifade eder
    na_name: Eksik gözlem barındıran değişkenleri ifade eder

    Returns
    -------
    Eğer na_name parametleri True olarak girildiyse eksik gözlem barındıran değişkenleri liste olarak return eder

    Notes
    -------
    Fonksiyonun numpy ve pandas kütüphanelerine bağımlılığı vardır.

    """
    na_columns = [col for col in dataframe.columns if dataframe[col].isnull().sum() > 0]

    n_miss = dataframe[na_columns].isnull().sum().sort_values(ascending=False)
    ratio = (dataframe[na_columns].isnull().sum() / dataframe.shape[0] * 100).sort_values(ascending=False)
    missing_df = pd.concat([n_miss, np.round(ratio, 2)], axis=1, keys=['n_miss', 'ratio'])
    print(missing_df, end="\n")

    if na_name:
        return na_columns


def missing_vs_target(dataframe, target, na_columns):
    """

    Fonksiyon, veri setinde yer alan eksik gözlem barındıran değişkenlerin eksiklik durumlarına göre hedef değişken
    karşısındaki ortalama ve adet bilgilerini getirir

    Parameters
    ----------
    dataframe: Veri setini ifade eder.
    target: Hedef değişkeni ifade eder.
    na_columns: Eksik gözlem barındıran değişkenleri ifade eder.

    Returns
    -------
    Herhangi bir değer return etmez.

    Notes
    -------
    Fonksiyonun numpy ve pandas kütüphanelerine bağımlılığı vardır.
    """
    temp_df = dataframe.copy()

    for col in na_columns:
        temp_df[col + '_NA_FLAG'] = np.where(temp_df[col].isnull(), 1, 0)

    na_flags = temp_df.loc[:, temp_df.columns.str.contains("_NA_")].columns

    for col in na_flags:
        print(pd.DataFrame({"TARGET_MEAN": temp_df.groupby(col)[target].mean(),
                            "Count": temp_df.groupby(col)[target].count()}), end="\n\n\n")


def label_encoder(dataframe, binary_col):
    """
    Fonksiyon verilen veri setindeki ilgili değişkenleri label encoding sürecine tabii tutar.

    Parameters
    ----------
    dataframe: Veri setini ifade eder.
    binary_col: Encode edilecek olaran değişkenleri ifade eder

    Returns
    -------
    Encoding işlemi yapılmiş bir şekilde "dataframe"i return eder

    Notes
    -------
    Fonksiyonun "from sklearn.preprocessing import LabelEncoder" paketine bağımlılığı bulunmaktadır.

    """
    labelencoder = LabelEncoder()
    dataframe[binary_col] = labelencoder.fit_transform(dataframe[binary_col])
    return dataframe


def one_hot_encoder(dataframe, categorical_cols, drop_first=True):
    """

    Veri setindeki kategorik değşkenler için one hot encoding işlemini yapar

    Parameters
    ----------
    dataframe : Veri setini ifade eder
    categorical_cols : Kategorik değişkenleri ifade eder
    drop_first : Dummy değişken tuzağına düşmemek için ilk değşşkeni siler

    Returns
    -------
    One-hot encoding işlemi yapılmış bir şekilde "dataframe"i return eder

    Notes
    -------
    Fonksiyonun "pandas" kütüphanesine bağımlılığı bulunmaktadır.
    """
    dataframe = pd.get_dummies(dataframe, columns=categorical_cols, drop_first=drop_first)
    return dataframe


def cat_summary(dataframe, col_name, plot=False):
    """

    Fonksiyon, veri setinde yer alan kategorik, numerik vs... şeklinde gruplandırılan değişkenler için özet bir çıktı
    sunar.

    Parameters
    ----------
    dataframe : Veri setini ifade
    col_name : Değişken grubunu ifade eder
    plot : Çıktı olarak bir grafik istenip, istenmediğini ifade eder, defaul olarak "False" gelir

    Returns
    -------
    Herhangi bir değer return etmez

    Notes
    -------
    Fonksiyonun pandas, seaborn ve matplotlib kütüphanelerine bağımlılığı vardır.

    """
    print(pd.DataFrame({col_name: dataframe[col_name].value_counts(),
                        "Ratio": 100 * dataframe[col_name].value_counts() / len(dataframe)}))
    print("##########################################")
    if plot:
        sns.countplot(x=dataframe[col_name], data=dataframe)
        plt.show()


def rare_analyser(dataframe, target, cat_cols):
    """
    Verilen veri setindeki hedef değişkene göre değişken grubundaki nadir gözlemleri analiz eder
    Parameters
    ----------
    dataframe : Veri setini ifade eder.
    target : Hedef değişkeni ifade eder.
    cat_cols : Değişken grubunu ifade eder

    Returns
    -------
    Herhangi bir değer retrun etmez.
    """
    for col in cat_cols:
        print(col, ":", len(dataframe[col].value_counts()))
        print(pd.DataFrame({"COUNT": dataframe[col].value_counts(),
                            "RATIO": dataframe[col].value_counts() / len(dataframe),
                            "TARGET_MEAN": dataframe.groupby(col)[target].mean()}), end="\n\n\n")


# rare_analyser(df, "TARGET", cat_cols)

def rare_encoder(dataframe, rare_perc):
    """

    Verilen veri setinde, önceden verilen orana göre rare encoding işlemi yapar

    Parameters
    ----------
    dataframe : Veri setini ifade eder.
    rare_perc : Nadir görülme oranını ifade eder.

    Returns
    -------
    Rare encoding yapılmış datafremi return eder
    """
    temp_df = dataframe.copy()

    rare_columns = [col for col in temp_df.columns if temp_df[col].dtypes == 'O'
                    and (temp_df[col].value_counts() / len(temp_df) < rare_perc).any(axis=None)]

    for var in rare_columns:
        tmp = temp_df[var].value_counts() / len(temp_df)
        rare_labels = tmp[tmp < rare_perc].index
        temp_df[var] = np.where(temp_df[var].isin(rare_labels), 'Rare', temp_df[var])

    return temp_df


def score_pos_neg_diff(pos, neg):
    return pos - neg


#df["score_pos_neg_diff"] = score_pos_neg_diff(df["helpful_yes"], df["helpful_no"])


def score_average_rating(pos, neg):
    if pos + neg == 0:
        return 0
    return pos / (pos + neg)


#df["score_average_rating"] = df.apply(lambda x: score_average_rating(x["helpful_yes"], x["helpful_no"]), axis=1)

'''
def plot_importance(model, features, num=len(X), save=False):
    feature_imp = pd.DataFrame({'Value': model.feature_importances_, 'Feature': features.columns})
    plt.figure(figsize=(10, 10))
    sns.set(font_scale=1)
    sns.barplot(x="Value", y="Feature", data=feature_imp.sort_values(by="Value",
                                                                      ascending=False)[0:num])
    plt.title('Features')
    plt.tight_layout()
    plt.show()
    if save:
        plt.savefig('importances.png')


#plot_importance(rf_model, X_train)
'''


def wilson_lower_bound(pos, neg, confidence=0.95):
    n = pos + neg
    if n == 0:
        return 0
    z = st.norm.ppf(1 - (1 - confidence) / 2)
    phat = 1.0 * pos / n
    return (phat + z * z / (2 * n) - z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)) / (1 + z * z / n)


#df["wilson_lower_bound"] = df.apply(lambda x: wilson_lower_bound(x["helpful_yes"], x["helpful_no"]), axis=1)

#df.head()


def item_based_recommender(movie_name, user_movie_df):
    movie = user_movie_df[movie_name]
    return user_movie_df.corrwith(movie).sort_values(ascending=False).head(10)


def create_user_movie_df():
    import pandas as pd
    movie = pd.read_csv(r'C:\Users\NerminB\PycharmProjects\pythonProject1\dataset\movie.csv')
    rating = pd.read_csv(r'C:\Users\NerminB\PycharmProjects\pythonProject1\dataset\rating.csv')
    df = movie.merge(rating, how="left", on="movieId")
    comment_counts = pd.DataFrame(df["title"].value_counts())
    rare_movies = comment_counts[comment_counts["count"] <= 1000].index
    common_movies = df[~df["title"].isin(rare_movies)]
    user_movie_df = common_movies.pivot_table(index=["userId"], columns=["title"], values="rating")
    return user_movie_df


#user_movie_df = create_user_movie_df()

#user_movie_df.head()


def arl_recommender(rules_df, product_id, rec_count=1):
    sorted_rules = rules_df.sort_values("lift", ascending=False)
    # kuralları lifte göre büyükten kücüğe sıralar. (en uyumlu ilk ürünü yakalayabilmek için)
    # confidence'e göre de sıralanabilir insiyatife baglıdır.
    recommendation_list = []  # tavsiye edilecek ürünler için bos bir liste olusturuyoruz.
    # antecedents: X
    #items denildigi için frozenset olarak getirir. index ve hizmeti birleştirir.
    # i: index
    # product: X yani öneri isteyen hizmet
    for i, product in sorted_rules["antecedents"].items():
        for j in list(product):  # hizmetlerde(product) gez:
            if j == product_id:  # eger tavsiye istenen ürün yakalanırsa:
                recommendation_list.append(list(sorted_rules.iloc[i]["consequents"]))
                # index bilgisini i ile tutuyordun bu index bilgisindeki consequents(Y) değerini recommendation_list'e ekle.
    # tavsiye listesinde tekrarlamayı önlemek için:
    # mesela 2'li 3'lü kombinasyonlarda aynı ürün tekrar düşmüş olabilir listeye gibi;
    # sözlük yapısının unique özelliginden yararlanıyoruz.
    recommendation_list = list({item for item_list in recommendation_list for item in item_list})
    return recommendation_list[:rec_count]  # :rec_count istenen sayıya kadar tavsiye ürün getir.


#arl_recommender(rules,"2_0", 3)


def check_skew(df_skew, column):
    skew = stats.skew(df_skew[column])
    skewtest = stats.skewtest(df_skew[column])
    plt.title('Distribution of ' + column)
    sns.displot(df_skew[column])
    print("{}'s: Skew: {}, : {}".format(column, skew, skewtest))
    return


def val_curve_params(model, X, y, param_name, param_range, scoring="roc_auc", cv=10):
    train_score, test_score = validation_curve(
        model, X=X, y=y, param_name=param_name, param_range=param_range, scoring=scoring, cv=cv)

    mean_train_score = np.mean(train_score, axis=1)
    mean_test_score = np.mean(test_score, axis=1)

    plt.plot(param_range, mean_train_score,
             label="Training Score", color='b')

    plt.plot(param_range, mean_test_score,
             label="Validation Score", color='g')

    plt.title(f"Validation Curve for {type(model).__name__}")
    plt.xlabel(f"Number of {param_name}")
    plt.ylabel(f"{scoring}")
    plt.tight_layout()
    plt.legend(loc='best')
    plt.show()


'''
rf_val_params = [["max_depth", [5, 8, 15, 20, 30, None]],
                 ["max_features", [3, 5, 7, "auto"]],
                 ["min_samples_split", [2, 5, 8, 15, 20]],
                 ["n_estimators", [10, 50, 100, 200, 500]]]


rf_model = RandomForestRegressor(random_state=17)

for i in range(len(rf_val_params)):
    val_curve_params(rf_model, X, y, rf_val_params[i][0], rf_val_params[i][1],scoring="neg_mean_absolute_error")

rf_val_params[0][1]
'''


def quick_missing_imp(data, num_method="median", cat_length=20, target="SalePrice"):
    variables_with_na = [col for col in data.columns if
                         data[col].isnull().sum() > 0]  # Eksik değere sahip olan değişkenler listelenir

    temp_target = data[target]

    print("# BEFORE")
    print(data[variables_with_na].isnull().sum(), "\n\n")  # Uygulama öncesi değişkenlerin eksik değerlerinin sayısı

    # değişken object ve sınıf sayısı cat_lengthe eşit veya altındaysa boş değerleri mode ile doldur
    data = data.apply(lambda x: x.fillna(x.mode()[0]) if (x.dtype == "O" and len(x.unique()) <= cat_length) else x,
                      axis=0)

    # num_method mean ise tipi object olmayan değişkenlerin boş değerleri ortalama ile dolduruluyor
    if num_method == "mean":
        data = data.apply(lambda x: x.fillna(x.mean()) if x.dtype != "O" else x, axis=0)
    # num_method median ise tipi object olmayan değişkenlerin boş değerleri ortalama ile dolduruluyor
    elif num_method == "median":
        data = data.apply(lambda x: x.fillna(x.median()) if x.dtype != "O" else x, axis=0)

    data[target] = temp_target

    print("# AFTER \n Imputation method is 'MODE' for categorical variables!")
    print(" Imputation method is '" + num_method.upper() + "' for numeric variables! \n")
    print(data[variables_with_na].isnull().sum(), "\n\n")

    return data


#df = quick_missing_imp(df, num_method="median", cat_length=17)

def create_stress_response_feature(row):
    if row['Growing_Stress'] == 'Yes' and row['Changes_Habits'] in ['Yes', 'Maybe']:
        return 'High'
    elif row['Growing_Stress'] == 'Maybe' or row['Changes_Habits'] == 'Maybe':
        return 'Medium'
    else:
        return 'Low'


def stress_concentration_interaction(row):
    if row['Growing_Stress'] == 'Yes' and row['Concentration'] in ['1 From 10', '2 From 10', '3 From 10']:
        return 'HighStress_LowConcentration'
    elif row['Growing_Stress'] == 'No' and row['Concentration'] in ['8 From 10', '9 From 10', '10 From 10']:
        return 'LowStress_HighConcentration'
    else:
        return 'Other'


def psychological_response_habits_interaction(row):
    if row['Aggressive Response'] == 'YES' and row['Changes_Habits'] == 'Yes':
        return 'Aggressive_ChangeHabits'
    elif row['Aggressive Response'] == 'NO' and row['Changes_Habits'] == 'No':
        return 'Calm_KeepHabits'
    else:
        return 'Mixed'


def family_history_treatment_interaction(row):
    if row['family_history'] == 'Yes' and row['treatment'] == 'Yes':
        return 'FamilyHistory_Treatment'
    elif row['family_history'] == 'No' and row['treatment'] == 'No':
        return 'NoFamilyHistory_NoTreatment'
    else:
        return 'Other'


def occupation_stress_level_interaction(row):
    if row['Occupation'] in ['Corporate', 'Student'] and row['Growing_Stress'] == 'Yes':
        return 'HighStress_Job'
    elif row['Occupation'] in ['Housewife', 'Others'] and row['Growing_Stress'] == 'No':
        return 'LowStress_Job'
    else:
        return 'Other'


def extract_number_from_string(dataframe, col):
    # String değerleri sayısal değerlere dönüştürme
    dataframe[col] = dataframe[col].str.split().str[0]
    dataframe[col] = pd.to_numeric(dataframe[col])
    return dataframe
