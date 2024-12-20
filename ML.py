# -*- coding: utf-8 -*-
"""Bangalore_Housing_Price_Prediction.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1d_A_ckho50NU0s0X85i_ps80yMieW3sf

### Importing Libraries
"""

import streamlit as st
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import matplotlib
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score, ShuffleSplit
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
# Streamlit app header
st.title("Machine Learning App")

# Display instructions or information
st.write("This is a basic Streamlit app for running machine learning models and visualizing data.")

# Example: Generating and displaying a plot
# Create random data for demonstration
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Plot the data
plt.figure(figsize=(10, 5))
plt.plot(x, y, label='Sine Wave')
plt.title('Sample Plot')
plt.xlabel('X')
plt.ylabel('Y')
plt.legend()

# Display the plot in the Streamlit app
st.pyplot(plt)

# User input example
# You can use Streamlit widgets for user interaction
user_input = st.text_input("Enter a value:")
if user_input:
    st.write(f"You entered: {user_input}")

# Select a model for training
option = st.selectbox(
    "Choose a model to train",
    ["Linear Regression", "Random Forest Regressor", "Gradient Boosting Regressor"]
)

# Display the selected model
st.write(f"You selected: {option}")

# Example: Load a dataset and split into training and testing sets
# Replace with your actual dataset and preprocessing
from sklearn.datasets import make_regression

X, y = make_regression(n_samples=100, n_features=1, noise=0.1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the selected model
if st.button("Run Model"):
    if option == "Linear Regression":
        model = LinearRegression()
    elif option == "Random Forest Regressor":
        model = RandomForestRegressor()
    elif option == "Gradient Boosting Regressor":
        model = GradientBoostingRegressor()

    # Fit the model
    model.fit(X_train, y_train)

    # Predict and evaluate
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Display evaluation results
    st.write("Mean Squared Error:", mse)
    st.write("R-squared Score:", r2)

    # Optional: Plot predictions vs actual values
    plt.figure(figsize=(10, 5))
    plt.scatter(X_test, y_test, color='blue', label='Actual')
    plt.scatter(X_test, y_pred, color='red', label='Predicted')
    plt.title('Actual vs Predicted Values')
    plt.xlabel('X')
    plt.ylabel('y')
    plt.legend()
    st.pyplot(plt)


"""<h2 style='color:blue'>Data Load: Load banglore home prices into a dataframe</h2>"""



df1 = pd.read_csv('bengaluru_house_prices.csv')
df1.head()

df1.head()

df1.shape

df1['area_type'].value_counts()

"""**Drop features that are not required to build our model**"""

df2 = df1.drop(['society','availability'],axis='columns')
df2.shape

"""<h2 style='color:blue'>Data Cleaning: Handle NA values</h2>"""

df2.isnull().sum()

df3 = df2.dropna()

df3.shape

print(df3.dtypes)

# Remove any non-numeric characters (such as spaces or commas) and convert to numeric
df3['total_sqft'] = df3['total_sqft'].replace(r'\D', '', regex=True)  # Remove non-numeric characters

# Convert 'total_sqft' to numeric (float) and handle errors gracefully
df3['total_sqft'] = pd.to_numeric(df3['total_sqft'], errors='coerce')

df3.loc[:, 'bhk'] = df3['size'].apply(lambda x: int(x.split(' ')[0]))

df3.bhk.unique()

# Descriptive statistics of the dataset
df3.describe()

"""outlier detected, house having 40 bath or 43 bedroom is not normal"""

import matplotlib.pyplot as plt

# Plotting the price distribution
plt.figure(figsize=(10,6))
plt.hist(df2['price'], bins=50, color='skyblue', edgecolor='black')
plt.title('Price Distribution')
plt.xlabel('Price (in Lakhs)')
plt.ylabel('Frequency')
plt.show()

"""right-skewed"""

# Scatter plot for Price vs. Total Square Footage
plt.figure(figsize=(10,6))
plt.scatter(df2['total_sqft'], df2['price'], alpha=0.5, color='green')
plt.title('Price vs. Total Square Footage')
plt.xlabel('Total Square Footage')
plt.ylabel('Price (in Lakhs)')
plt.show()

"""this also shows some outlier that can be removed"""

# Boxplot for Price vs. BHK
plt.figure(figsize=(10,6))
df3.boxplot(column='price', by='bhk', vert=False)
plt.title('Price vs. Number of Bedrooms (BHK)')
plt.suptitle('')
plt.xlabel('Price (in Lakhs)')
plt.ylabel('Number of Bedrooms (BHK)')
plt.show()

"""some prices are not consistent with the number of bedrooms,outlier"""

import seaborn as sns

# Correlation matrix
df_numeric = df3.select_dtypes(include=['number'])
corr_matrix = df_numeric.corr()

# Plotting the correlation matrix
plt.figure(figsize=(12,8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title('Correlation Matrix')
plt.show()

"""high corollation between price with bath and bedroom

<h2 style='color:blue'>Feature Engineering</h2>

**Add new feature(integer) for bhk (Bedrooms Hall Kitchen)**
"""

df3

def convert_sqft_to_num(x):
    tokens = x.split('-')
    if len(tokens) == 2:
        return (float(tokens[0])+float(tokens[1]))/2
    try:
        return float(x)
    except:
        return None

df4 = df3.copy()
df4 = df4[df4.total_sqft.notnull()]
df4.head(2)

"""**Add new feature called price per square feet**"""

df5 = df4.copy()
df5['price_per_sqft'] = df5['price']*100000/df5['total_sqft']
df5.head()

df5.to_csv("bhp.csv",index=False)

"""**Examine locations which is a categorical variable. We need to apply dimensionality reduction technique here to reduce number of locations**"""

df5.location = df5.location.apply(lambda x: x.strip())
location_stats = df5['location'].value_counts(ascending=False)
location_stats

location_stats.values.sum()

len(location_stats[location_stats>10])

len(location_stats)

"""<h2 style="color:blue">Dimensionality Reduction</h2>

**Any location having less than 10 data points will be tagged as "other" location. This way number of categories can be reduced by huge amount. It will help us with having fewer dummy columns**
"""

location_stats_less_than_10 = location_stats[location_stats<=10]

df5.location = df5.location.apply(lambda x: 'other' if x in location_stats_less_than_10 else x)
len(df5.location.unique())

"""<h2 style="color:blue">Outlier Removal Using Logic</h2>

**Normally square ft per bedroom is 300 (i.e. 2 bhk apartment is minimum 600 sqft. Example 400 sqft apartment with 2 bhk than that seems suspicious and can be removed as an outlier. We will remove such outliers by keeping our minimum thresold per bhk to be 300 sqft**
"""

df5[df5.total_sqft/df5.bhk<300].head()

df5.shape

df5.price_per_sqft.describe()

"""**Here we find that min price per sqft is 267 rs/sqft whereas max is 176470, this shows a wide variation in property prices. We should remove outliers per location using mean and one standard deviation**"""

def remove_pps_outliers(df):
    df_out = pd.DataFrame()
    for key, subdf in df.groupby('location'):
        m = np.mean(subdf.price_per_sqft)
        st = np.std(subdf.price_per_sqft)
        reduced_df = subdf[(subdf.price_per_sqft>(m-st)) & (subdf.price_per_sqft<=(m+st))]
        df_out = pd.concat([df_out,reduced_df],ignore_index=True)
    return df_out
df6 = remove_pps_outliers(df5)
df6.shape

"""**Let's check if for a given location how does the 2 BHK and 3 BHK property prices look like**"""

def plot_scatter_chart(df,location):
    bhk2 = df[(df.location==location) & (df.bhk==2)]
    bhk3 = df[(df.location==location) & (df.bhk==3)]
    matplotlib.rcParams['figure.figsize'] = (15,10)
    plt.scatter(bhk2.total_sqft,bhk2.price,color='blue',label='2 BHK', s=50)
    plt.scatter(bhk3.total_sqft,bhk3.price,marker='+', color='green',label='3 BHK', s=50)
    plt.xlabel("Total Square Feet Area")
    plt.ylabel("Price (Lakh Indian Rupees)")
    plt.title(location)
    plt.legend()

plot_scatter_chart(df6,"Rajaji Nagar")

plot_scatter_chart(df6,"Hebbal")

import matplotlib
matplotlib.rcParams["figure.figsize"] = (20,10)
plt.hist(df6.price_per_sqft,rwidth=0.8)
plt.xlabel("Price Per Square Feet")
plt.ylabel("Count")

"""<h2 style='color:blue'>Outlier Removal Using Bathrooms Feature</h2>"""

df6.bath.unique()

plt.hist(df6.bath,rwidth=0.8)
plt.xlabel("Number of bathrooms")
plt.ylabel("Count")

df6[df6.bath>10]

"""**It is unusual to have 2 more bathrooms than number of bedrooms in a home**"""

df6[df6.bath>df6.bhk+2]

df7 = df6[df6.bath<df6.bhk+2]
df7.shape

df8 = df7.drop(['size'], axis='columns')
df8.head(3)

"""<h2 style='color:blue'>Use One Hot Encoding For Location and Area</h2>"""

area_type_dummies = pd.get_dummies(df8['area_type'], drop_first=True)
location_dummies = pd.get_dummies(df8['location'], drop_first=True)
df8

df9 = pd.concat([df8, area_type_dummies, location_dummies], axis='columns')
df9.head()

df10 = df9.drop(['area_type', 'location'], axis='columns')

df10

"""<h2 style='color:blue'>Build a Model Now...</h2>"""

X = df10.drop(['price'],axis='columns')
y = df10.price

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=10)

from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, ShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import numpy as np

# Feature Scaling (StandardScaler for Linear Regression)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Model 1: Linear Regression
lr = LinearRegression()
lr.fit(X_train_scaled, y_train)
y_train_pred_lr = lr.predict(X_train_scaled)
y_test_pred_lr = lr.predict(X_test_scaled)

# Model 2: Random Forest
rf = RandomForestRegressor(random_state=42)
rf.fit(X_train, y_train)
y_train_pred_rf = rf.predict(X_train)
y_test_pred_rf = rf.predict(X_test)

# Model 3: Gradient Boosting
gb = GradientBoostingRegressor(random_state=42)
gb.fit(X_train, y_train)
y_train_pred_gb = gb.predict(X_train)
y_test_pred_gb = gb.predict(X_test)

# Model Performance Evaluation (R², RMSE)
def evaluate_model(y_true, y_pred):
    r2 = r2_score(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    return r2, rmse

# Evaluation for Linear Regression
r2_train_lr, rmse_train_lr = evaluate_model(y_train, y_train_pred_lr)
r2_test_lr, rmse_test_lr = evaluate_model(y_test, y_test_pred_lr)

# Evaluation for Random Forest
r2_train_rf, rmse_train_rf = evaluate_model(y_train, y_train_pred_rf)
r2_test_rf, rmse_test_rf = evaluate_model(y_test, y_test_pred_rf)

# Evaluation for Gradient Boosting
r2_train_gb, rmse_train_gb = evaluate_model(y_train, y_train_pred_gb)
r2_test_gb, rmse_test_gb = evaluate_model(y_test, y_test_pred_gb)

# Print Results
print("Linear Regression - Training R²: {:.4f}, RMSE: {:.4f} | Testing R²: {:.4f}, RMSE: {:.4f}".format(
    r2_train_lr, rmse_train_lr, r2_test_lr, rmse_test_lr))
print("Random Forest - Training R²: {:.4f}, RMSE: {:.4f} | Testing R²: {:.4f}, RMSE: {:.4f}".format(
    r2_train_rf, rmse_train_rf, r2_test_rf, rmse_test_rf))
print("Gradient Boosting - Training R²: {:.4f}, RMSE: {:.4f} | Testing R²: {:.4f}, RMSE: {:.4f}".format(
    r2_train_gb, rmse_train_gb, r2_test_gb, rmse_test_gb))

"""<h2 style='color:blue'>Find best model using GridSearchCV</h2>"""

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

# Split the data into training, validation, and test sets
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

# Define parameter distributions for RandomizedSearchCV
param_dist = {
    'n_estimators': [20, 50, 100, 200, 500,1000],  # Number of trees
    'max_depth': [None, 10, 20, 30, 40, 50],  # Maximum depth of the tree
    'min_samples_split': [2, 5, 10, 20],  # Minimum samples required to split a node
    'min_samples_leaf': [1, 2, 4, 6],  # Minimum samples required at a leaf node
    'bootstrap': [True, False]  # Whether to use bootstrap sampling
}

# Initialize Random Forest model
rf = RandomForestRegressor(random_state=42)

# Initialize RandomizedSearchCV
random_search = RandomizedSearchCV(
    rf, param_distributions=param_dist,
    n_iter=10,  # Number of random combinations to try
    cv=5,  # 5-fold cross-validation
    verbose=2,  # Verbosity level to show progress
    random_state=42,
    n_jobs=-1,  # Use all available CPU cores
    scoring='neg_mean_squared_error'  # Score by negative MSE (can also use R²)
)

# Fit RandomizedSearchCV on the training data
random_search.fit(X_train, y_train)

# Get the best parameters and model
best_params = random_search.best_params_
best_model = random_search.best_estimator_

# Make predictions using the best model on the validation set
y_val_pred = best_model.predict(X_val)

# Evaluate the model on the validation set
r2_val = r2_score(y_val, y_val_pred)
rmse_val = np.sqrt(mean_squared_error(y_val, y_val_pred))

# Print the best parameters and validation set performance
print(f"Best parameters for Random Forest: {best_params}")
print(f"Validation Set - R²: {r2_val:.4f}, RMSE: {rmse_val:.4f}")

# Once the best model is selected based on validation set performance, test it on the test set
y_test_pred = best_model.predict(X_test)

# Evaluate the model on the test set
r2_test = r2_score(y_test, y_test_pred)
rmse_test = np.sqrt(mean_squared_error(y_test, y_test_pred))

# Print the performance on the test set
print(f"Test Set - R²: {r2_test:.4f}, RMSE: {rmse_test:.4f}")

from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import GradientBoostingRegressor

# Define the model
gb = GradientBoostingRegressor(random_state=42)

# Define the parameter grid
param_dist = {
    'n_estimators': [50, 100, 200, 300, 500],
    'learning_rate': [0.01, 0.05, 0.1, 0.2],
    'max_depth': [3, 4, 5, 6, 7],
    'subsample': [0.7, 0.8, 0.9, 1.0],
    'min_samples_split': [2, 5, 10],
}

# Set up the random search with cross-validation
random_search = RandomizedSearchCV(
    gb, param_distributions=param_dist, n_iter=10, cv=5, verbose=2, random_state=42, n_jobs=-1
)

# Fit the model
random_search.fit(X_train, y_train)

# Get the best parameters and model
best_model = random_search.best_estimator_
print("Best hyperparameters:", random_search.best_params_)

y_train_pred = best_model.predict(X_train)
y_test_pred = best_model.predict(X_test)

# Evaluate the model on the training set
r2_train = r2_score(y_train, y_train_pred)
rmse_train = np.sqrt(mean_squared_error(y_train, y_train_pred))

# Evaluate the model on the testing set
r2_test = r2_score(y_test, y_test_pred)
rmse_test = np.sqrt(mean_squared_error(y_test, y_test_pred))

# Print the results
print("Training Set - R²: {:.4f}, RMSE: {:.4f}".format(r2_train, rmse_train))
print("Testing Set - R²: {:.4f}, RMSE: {:.4f}".format(r2_test, rmse_test))



import shap

explainer = shap.TreeExplainer(best_model)
shap_values = explainer.shap_values(X_test)  # Use the same preprocessed X_test

# Plot summary of feature importance
shap.summary_plot(shap_values, X_test)

shap.initjs()
# Visualize the SHAP values for a single prediction
shap.force_plot(explainer.expected_value, shap_values[0], X_test.iloc[0])

# Decision plot for cumulative feature contributions for a single sample
shap.decision_plot(explainer.expected_value, shap_values[0], X_test.iloc[0])
