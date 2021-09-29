# -*- coding: utf-8 -*-
"""ksi_analysis.ipynb

# Toronto Traffic Accident Analysis

- Daniel Siegel - 101367445
- Michael McAllister - 101359469
- Hom Kandel - 101385341
- Eduardo Bastos de Moraes - 101345799

## Project Definition:

For this project, we were expected to build either a Random Forest Classifier or a Random Forest Regressor. This model is meant to analyze a database with the following 3 criteria:

1.	The database needs to have at least 2 classes
2.	The database should at least have 300 samples/rows
3.	The database should at least have 8 columns/features

Report:
Put your results in a report. Your report needs to include the following sections:
•	The Problem statement,
•	The Database,
•	The model you picked to solve the problem,
•	Results, the model performance (test, valid), the loss, predictions…
(like use of confusion matrices etc…)
•	Conclusions

In your results please comment and discuss the followings:
1.	Evaluate the model, how?
2.	How your model change when the number of estimators (decision trees) changes?
3.	What is the best number of estimators? How you can select the best number of estimators?

# Problem Statement

For our project, we have decided to analyze the Killed or Seriously Injured (KSI) database if we can determine the conditions most likely to lead to fatality.

# Import the database and libraries
"""

import pandas as pd
import numpy as np
import pandas_profiling
import seaborn as sns
from matplotlib import pyplot as plt

data = pd.read_csv('https://raw.githubusercontent.com/eduardomoraes/KSI/main/KSI_CLEAN.csv')

"""# Initial observations of the dataset"""

# Criteria 1: At least 2 classes. We have ~11,000 rows of class A, ~2000 rows of class B, and a very small class C.
print("The target class, INJURY - the injury suffered by each person in the accident")
data['INJURY'].value_counts()

# Criteria 2 & 3: over 300 rows and 8 or more columns/features
print('The dataset has', data.shape[0], 'rows and', data.shape[1], 'columns.')

pd.set_option('display.max_columns', None)
data.head()

data.info()

# At first glance the data appears to be very clean
plt.figure(figsize=(20,5))
sns.heatmap(data.isna(), cbar=False, cmap='viridis', yticklabels=False)

#After trying numerous times to try and figure out the blanks values in the database, they've been setup as ' ' strings which hid blank values
plt.figure(figsize=(20,5))
sns.heatmap(data.eq(' '), cbar=False, cmap='viridis', yticklabels=False)

"""# Cleaning The Data"""

# Drop superfluous columns - some with irrelevant data, some with duplicate information (such as "FATAL_NO")
data = data.drop(['YEAR', 'MONTH', 'DAY', 'HOUR', 'MINUTES', 'LATITUDE', 'LONGITUDE', 'Ward_Name', 'Hood_Name', 'Division', 'District', 'STREET1', 'STREET2', 'OFFSET', 'INITDIR', 'ACCLASS', 'FATAL_NO'], axis=1)
data.info()

for column_name in ['FATAL','DISABILITY', 'ALCOHOL', 'REDLIGHT',
                    'AG_DRIV', 'SPEEDING', 'PASSENGER', 'EMERG_VEH',
                    'TRSN_CITY_VEH', 'TRUCK', 'MOTORCYCLE', 'AUTOMOBILE',
                    'CYCLIST', 'PEDESTRIAN']:
    data[column_name] = data[column_name].astype('int64')

# Clean ROAD_CLASS column (hich type of road the drivers were on) was setup as an ordinal feature
data['ROAD_CLASS'] = data['ROAD_CLASS'].replace(to_replace=['Minor Arterial', 'Laneway', 'Local'], value=0, inplace=False, limit=None, regex=False, method='pad')
data['ROAD_CLASS'] = data['ROAD_CLASS'].replace(to_replace=['Major Arterial', 'Major Arterial Ramp'], value=1, inplace=False, limit=None, regex=False, method='pad')
data['ROAD_CLASS'] = data['ROAD_CLASS'].replace(to_replace=['Collector', 'Expressway', 'Expressway Ramp'], value=2, inplace=False, limit=None, regex=False, method='pad')

# Clean VISIBILITY column (the weather conditions surrounding the accident) was setup as an ordinal feature
original_data = data['VISIBILITY'].value_counts()
data['VISIBILITY'] = data['VISIBILITY'].replace(to_replace=['Clear', 'Other', ' '], value=0, inplace=False, limit=None, regex=False, method='pad')
data['VISIBILITY'] = data['VISIBILITY'].replace(to_replace=['Rain', 'Strong wind', 'Fog, Mist, Smoke, Dust'], value=1, inplace=False, limit=None, regex=False, method='pad')
data['VISIBILITY'] = data['VISIBILITY'].replace(to_replace=['Snow', 'Freezing Rain', 'Drifting Snow'], value=2, inplace=False, limit=None, regex=False, method='pad')

# Clean LIGHT column (the amount of light present at the time of accident) was setup as an ordinal feature, Dusk and Dawn were merged due to similar lighting
data['LIGHT'] = data['LIGHT'].replace(to_replace=['Daylight', 'Daylight, artificial', ' ', 'Other'], value=0, inplace=False, limit=None, regex=False, method='pad')
data['LIGHT'] = data['LIGHT'].replace(to_replace=['Dusk', 'Dusk, artificial', 'Dawn', 'Dawn, artificial'], value=1, inplace=False, limit=None, regex=False, method='pad')
data['LIGHT'] = data['LIGHT'].replace(to_replace=['Dark', 'Dark, artificial'], value=2, inplace=False, limit=None, regex=False, method='pad')

# Clean RDSFCOND column (the road surface condition) was setup as an ordinal feature
data['RDSFCOND'] = data['RDSFCOND'].replace(to_replace=['Dry', ' '], value=0, inplace=False, limit=None, regex=False, method='pad')
data['RDSFCOND'] = data['RDSFCOND'].replace(to_replace=['Wet', 'Other', 'Loose Sand or Gravel', 'Loose Snow'], value=1, inplace=False, limit=None, regex=False, method='pad')
data['RDSFCOND'] = data['RDSFCOND'].replace(to_replace=['Slush', 'Ice', 'Packed Snow', 'Spilled liquid'], value=2, inplace=False, limit=None, regex=False, method='pad')

# Clean INVAGE column (age of involved party)
# setup ordinal list, and average filled unknown values
data['INVAGE'] = data['INVAGE'].replace(to_replace=['0 to 4'], value=0, inplace=False, limit=None, regex=False, method='pad')
data['INVAGE'] = data['INVAGE'].replace(to_replace=['5 to 9'], value=1, inplace=False, limit=None, regex=False, method='pad')
data['INVAGE'] = data['INVAGE'].replace(to_replace=['10 to 14'], value=2, inplace=False, limit=None, regex=False, method='pad')
data['INVAGE'] = data['INVAGE'].replace(to_replace=['15 to 19'], value=3, inplace=False, limit=None, regex=False, method='pad')
data['INVAGE'] = data['INVAGE'].replace(to_replace=['20 to 24'], value=4, inplace=False, limit=None, regex=False, method='pad')
data['INVAGE'] = data['INVAGE'].replace(to_replace=['25 to 29'], value=5, inplace=False, limit=None, regex=False, method='pad')
data['INVAGE'] = data['INVAGE'].replace(to_replace=['30 to 34'], value=6, inplace=False, limit=None, regex=False, method='pad')
data['INVAGE'] = data['INVAGE'].replace(to_replace=['35 to 39'], value=7, inplace=False, limit=None, regex=False, method='pad')
data['INVAGE'] = data['INVAGE'].replace(to_replace=['40 to 44'], value=8, inplace=False, limit=None, regex=False, method='pad')
data['INVAGE'] = data['INVAGE'].replace(to_replace=['45 to 49'], value=9, inplace=False, limit=None, regex=False, method='pad')
data['INVAGE'] = data['INVAGE'].replace(to_replace=['50 to 54'], value=10, inplace=False, limit=None, regex=False, method='pad')
data['INVAGE'] = data['INVAGE'].replace(to_replace=['55 to 59'], value=11, inplace=False, limit=None, regex=False, method='pad')
data['INVAGE'] = data['INVAGE'].replace(to_replace=['60 to 64'], value=12, inplace=False, limit=None, regex=False, method='pad')
data['INVAGE'] = data['INVAGE'].replace(to_replace=['65 to 69'], value=13, inplace=False, limit=None, regex=False, method='pad')
data['INVAGE'] = data['INVAGE'].replace(to_replace=['70 to 74'], value=14, inplace=False, limit=None, regex=False, method='pad')
data['INVAGE'] = data['INVAGE'].replace(to_replace=['75 to 79'], value=15, inplace=False, limit=None, regex=False, method='pad')
data['INVAGE'] = data['INVAGE'].replace(to_replace=['80 to 84'], value=16, inplace=False, limit=None, regex=False, method='pad')
data['INVAGE'] = data['INVAGE'].replace(to_replace=['85 to 89'], value=17, inplace=False, limit=None, regex=False, method='pad')
data['INVAGE'] = data['INVAGE'].replace(to_replace=['90 to 94'], value=18, inplace=False, limit=None, regex=False, method='pad')
data['INVAGE'] = data['INVAGE'].replace(to_replace=['Over 95'], value=19, inplace=False, limit=None, regex=False, method='pad')
data['INVAGE'] = data['INVAGE'].replace(to_replace=['unknown'], value=7, inplace=False, limit=None, regex=False, method='pad')

# Clean INJURY column (severity of injury)
# It appears that the injury code left blank means no injury, or the party is on the police report but indirectly involved in the accident so left blank
data.loc[data['INJURY'] == ' ']

# Injury will be our label, with ' ' values set to no injury
data['INJURY'] = data['INJURY'].replace(to_replace=['None', ' '], value=0, inplace=False, limit=None, regex=False, method='pad')
data['INJURY'] = data['INJURY'].replace(to_replace=['Minimal'], value=1, inplace=False, limit=None, regex=False, method='pad')
data['INJURY'] = data['INJURY'].replace(to_replace=['Minor'], value=2, inplace=False, limit=None, regex=False, method='pad')
data['INJURY'] = data['INJURY'].replace(to_replace=['Major'], value=3, inplace=False, limit=None, regex=False, method='pad')
data['INJURY'] = data['INJURY'].replace(to_replace=['Fatal'], value=4, inplace=False, limit=None, regex=False, method='pad')

# Clean VEHTYPE column - the type of vehicle involved.
# As we can see, pedestrian collisions have an other classifier very frequently.  However, it's also been tied to vehicle owners making this a difficult feature to clean
# As other is such a large category, I will not be changing this into an ordinal set as we lack the domain knowledge, and instead categorize using get_dummies.
# So we ended up grouping vehicle classes, leaving 'other' as it's own category, and leaving ' ' as it's own category
data['VEHTYPE'].value_counts()
data.loc[data['VEHTYPE'] == 'Other']

#Grouping small categories together by weight class/vehicle type
data['VEHTYPE'] = data['VEHTYPE'].replace(to_replace=[' '], value='NA', inplace=False, limit=None, regex=False, method='pad')
data['VEHTYPE'] = data['VEHTYPE'].replace(to_replace=['Municipal Transit Bus (TTC)', 'Truck - Open', 'Delivery Van', 'Street Car', 'Truck - Dump', 'Truck-Tractor', 'Bus (Other) (Go Bus, Gray Coach)', 'Truck (other)', 'Intercity Bus', 'Truck - Tank', 'School Bus', 'Construction Equipment', 'Truck - Car Carrier', 'Fire Vehicle', 'Other Emergency Vehicle'], value='Heavy Commercial', inplace=False, limit=None, regex=False, method='pad')
data['VEHTYPE'] = data['VEHTYPE'].replace(to_replace=['Off Road - 2 Wheels', 'Moped'], value='Motorcycle', inplace=False, limit=None, regex=False, method='pad')
data['VEHTYPE'] = data['VEHTYPE'].replace(to_replace=['Pick Up Truck', 'Passenger Van', 'Truck - Closed (Blazer, etc)', 'Tow Truck'], value='Large Auto', inplace=False, limit=None, regex=False, method='pad')
data['VEHTYPE'] = data['VEHTYPE'].replace(to_replace=['Taxi', 'Police Vehicle'], value='Automobile, Station Wagon', inplace=False, limit=None, regex=False, method='pad')

# Clean INVTYPE column - the involvement of the person in the row of the database
# Grouping small categories together by weight class/vehicle type
data['INVTYPE'] = data['INVTYPE'].replace(to_replace=['Moped Driver'], value='Motorcycle Driver', inplace=False, limit=None, regex=False, method='pad')
data['INVTYPE'] = data['INVTYPE'].replace(to_replace=['Motorcycle Passenger'], value='Motorcycle Driver', inplace=False, limit=None, regex=False, method='pad')
data['INVTYPE'] = data['INVTYPE'].replace(to_replace=['Wheelchair', 'In-Line Skater'], value='Pedestrian', inplace=False, limit=None, regex=False, method='pad')
data['INVTYPE'] = data['INVTYPE'].replace(to_replace=[' ', 'Other Property Owner', 'Driver - Not Hit', 'a', 'Runaway - No Driver', 'Unknown - FTR', 'Pedestrian - Not Hit', 'Witness'], value='Other', inplace=False, limit=None, regex=False, method='pad')
data['INVTYPE'] = data['INVTYPE'].replace(to_replace=['Trailer Owner'], value='Vehicle Owner', inplace=False, limit=None, regex=False, method='pad')

#Ordinal features and our label has now been setup, now we need to one hot encode all our categorical features
# Clean LOCCORD - Location Coordinates of accident
data['LOCCOORD'] = data['LOCCOORD'].replace(to_replace=[' ', 'Park, Private Property, Public Lane', 'Entrance Ramp Westbound'], value='Other', inplace=False, limit=None, regex=False, method='pad')
data1 = pd.get_dummies(data[['LOCCOORD']])
data = pd.concat([data,data1], axis=1)
data.drop('LOCCOORD', axis=1, inplace=True)

# Clean ACCLOC - the accident location
data['ACCLOC'] = data['ACCLOC'].replace(to_replace=[' '], value='Other', inplace=False, limit=None, regex=False, method='pad')
data1 = pd.get_dummies(data[['ACCLOC']])
data = pd.concat([data,data1], axis=1)
data.drop('ACCLOC', axis=1, inplace=True)

# Clean TRAFFCTL - the type of traffic control present
data1 = pd.get_dummies(data[['TRAFFCTL']])
data = pd.concat([data,data1], axis=1)
data.drop('TRAFFCTL', axis=1, inplace=True)

# Clean IMPACTYPE - the type of impact
data1 = pd.get_dummies(data[['IMPACTYPE']])
data = pd.concat([data,data1], axis=1)
data.drop('IMPACTYPE', axis=1, inplace=True)

# get_dummies for various columns
data1 = pd.get_dummies(data[['INVTYPE']])
data = pd.concat([data,data1], axis=1)
data.drop('INVTYPE', axis=1, inplace=True)

data1 = pd.get_dummies(data[['VEHTYPE']])
data = pd.concat([data,data1], axis=1)
data.drop('VEHTYPE', axis=1, inplace=True)

data1 = pd.get_dummies(data[['MANOEUVER']])
data = pd.concat([data,data1], axis=1)
data.drop('MANOEUVER', axis=1, inplace=True)

data1 = pd.get_dummies(data[['DRIVACT']])
data = pd.concat([data,data1], axis=1)
data.drop('DRIVACT', axis=1, inplace=True)

data1 = pd.get_dummies(data[['DRIVCOND']])
data = pd.concat([data,data1], axis=1)
data.drop('DRIVCOND', axis=1, inplace=True)

data1 = pd.get_dummies(data[['PEDTYPE']])
data = pd.concat([data,data1], axis=1)
data.drop('PEDTYPE', axis=1, inplace=True)

data1 = pd.get_dummies(data[['PEDACT']])
data = pd.concat([data,data1], axis=1)
data.drop('PEDACT', axis=1, inplace=True)

data1 = pd.get_dummies(data[['PEDCOND']])
data = pd.concat([data,data1], axis=1)
data.drop('PEDCOND', axis=1, inplace=True)

data1 = pd.get_dummies(data[['CYCLISTYPE']])
data = pd.concat([data,data1], axis=1)
data.drop('CYCLISTYPE', axis=1, inplace=True)

data1 = pd.get_dummies(data[['CYCACT']])
data = pd.concat([data,data1], axis=1)
data.drop('CYCACT', axis=1, inplace=True)

data1 = pd.get_dummies(data[['CYCCOND']])
data = pd.concat([data,data1], axis=1)
data.drop('CYCCOND', axis=1, inplace=True)

data.info()

data.head()

"""# Data Preprocessing"""

# string_columns=data.select_dtypes(include=[object])
# string_columns.head(5)

# from sklearn import preprocessing

# le = preprocessing.LabelEncoder()

# string_columns_transformed = string_columns.apply(le.fit_transform)
# string_columns_transformed.head()

# string_columns.shape

# string_columns_transformed.shape

# data = data.drop(columns=data.select_dtypes(['object']).columns)
#

# data.shape

# data=pd.concat([data,string_columns_transformed],axis=1)
# data.shape

# data.columns

# data['FATAL']

"""## Seletion of Best best features"""

# y=data.iloc[:,25]
#X=data.iloc[:,:-1]
# X = data.drop(columns=['FATAL', 'DISABILITY', 'ALCOHOL', 'REDLIGHT', 'AG_DRIV', 'SPEEDING', 'PASSENGER', 'EMERG_VEH', 'TRSN_CITY_VEH', 'TRUCK', 'MOTORCYCLE', 'AUTOMOBILE', 'CYCLIST', 'PEDESTRIAN', 'FATAL_NO', 'ACCNUM'])

# X.head(5)
# X.shape

"""#Applying Filter Feature Selection - Pearson Correlation"""

# feature_name = list(X.columns)
# no of maximum features we need to select
# num_feats=10


def corr_selector(X, y,num_feats):
    # Your code goes here (Multiple lines)
    corr_list = []
    feature_name = X.columns.tolist()

    for i in X.columns.tolist():
        cor = np.corrcoef(X[i], y)[0, 1]
        corr_list.append(cor)

    corr_list = [0 if np.isnan(i) else i for i in corr_list]

    corr_feature = X.iloc[:,np.argsort(np.abs(corr_list))[-num_feats:]].columns.tolist()

    corr_support = [True if i in corr_feature else False for i in feature_name]
    # Your code ends here
    return corr_support, corr_feature

# corr_support, corr_feature = corr_selector(X, y,num_feats)
# print(str(len(corr_feature)), 'selected features')

# corr_feature

"""#Appying Chi-Squared Selector function"""

from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.preprocessing import MinMaxScaler

def chi_squared_selector(X, y, num_feats):

    X_n = MinMaxScaler().fit_transform(X)
    chi_selector = SelectKBest(chi2, k=num_feats)
    chi_selector.fit(X_n, y)
    chi_support = chi_selector.get_support()
    chi_feature = X.loc[:,chi_support].columns.tolist()

    return chi_support, chi_feature

# chi_support, chi_feature = chi_squared_selector(X, y,num_feats)
# print(str(len(chi_feature)), 'selected features')

# chi_feature

"""#Appying Wrapper Feature Selection - Recursive Feature Elimination"""

from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MinMaxScaler

def rfe_selector(X, y, num_feats):
    # Your code goes here (Multiple lines)
    X_n = MinMaxScaler().fit_transform(X)
    rfe_selector = RFE(estimator=LogisticRegression(), n_features_to_select=num_feats, step=10, verbose=5)
    rfe_selector.fit(X_n, y)
    rfe_support = rfe_selector.get_support()
    rfe_feature = X.loc[:,rfe_support].columns.tolist()
    # Your code ends here
    return rfe_support, rfe_feature

# rfe_support, rfe_feature = rfe_selector(X, y,num_feats)
# print(str(len(rfe_feature)), 'selected features')

# rfe_feature

"""#Appying Embedded Selection - Lasso: SelectFromModel"""

from sklearn.feature_selection import SelectFromModel
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MinMaxScaler

def embedded_log_reg_selector(X, y, num_feats):
    # Your code goes here (Multiple lines)
    embedded_lr_selector = SelectFromModel(LogisticRegression(penalty="l2"), max_features=num_feats)
    embedded_lr_selector.fit(X, y)
    embedded_lr_support = embedded_lr_selector.get_support()
    embedded_lr_feature = X.loc[:,embedded_lr_support].columns.tolist()
    # Your code ends here
    return embedded_lr_support, embedded_lr_feature

# embedded_lr_support, embedded_lr_feature = embedded_log_reg_selector(X, y, num_feats)
# print(str(len(embedded_lr_feature)), 'selected features')

# embedded_lr_feature

"""#Appying Tree based(Random Forest): SelectFromModel"""

from sklearn.feature_selection import SelectFromModel
from sklearn.ensemble import RandomForestClassifier

def embedded_rf_selector(X, y, num_feats):
    # Your code goes here (Multiple lines)
    embedded_rf_selector = SelectFromModel(RandomForestClassifier(n_estimators=500), max_features=num_feats)
    embedded_rf_selector.fit(X, y)
    embedded_rf_support = embedded_rf_selector.get_support()
    embedded_rf_feature = X.loc[:,embedded_rf_support].columns.tolist()
    # Your code ends here
    return embedded_rf_support, embedded_rf_feature

# embedded_rf_support, embedded_rf_feature = embedded_rf_selector(X, y, num_feats)
# print(str(len(embedded_rf_feature)), 'selected features')

# embedded_rf_feature

"""#Appying Tree based(Light GBM): SelectFromModel"""

from sklearn.feature_selection import SelectFromModel
from lightgbm import LGBMClassifier

def embedded_lgbm_selector(X, y, num_feats):
    # Your code goes here (Multiple lines)
    lgbc=LGBMClassifier(n_estimators=500, learning_rate=0.05, num_leaves=32, colsample_bytree=0.2,
            reg_alpha=3, reg_lambda=1, min_split_gain=0.01, min_child_weight=40)

    embedded_lgbm_selector = SelectFromModel(lgbc, max_features=num_feats)
    embedded_lgbm_selector.fit(X, y)
    embedded_lgbm_support = embedded_lgbm_selector.get_support()
    embedded_lgbm_feature = X.loc[:,embedded_lgbm_support].columns.tolist()
    # Your code ends here
    return embedded_lgbm_support, embedded_lgbm_feature

# embedded_lgbm_support, embedded_lgbm_feature = embedded_lgbm_selector(X, y, num_feats)
# print(str(len(embedded_lgbm_feature)), 'selected features')

# embedded_lgbm_feature

"""#What are the best features?"""

# pd.set_option('display.max_rows', None)
# # put all selection together
# feature_selection_data = pd.DataFrame({'Feature':feature_name, 'Pearson':corr_support, 'Chi-2':chi_support, 'RFE':rfe_support, 'Logistics':embedded_lr_support,
#                                     'Random Forest':embedded_rf_support, 'LightGBM':embedded_lgbm_support})
# # count the selected times for each feature
# feature_selection_data['Total'] = np.sum(feature_selection_data, axis=1)
# # display the top 100
# feature_selection_data = feature_selection_data.sort_values(['Total','Feature'] , ascending=False)
# feature_selection_data.index = range(1, len(feature_selection_data)+1)
# feature_selection_data.head(num_feats)