import pandas as pd;
from datetime import datetime;
import matplotlib.pyplot as plt;
import numpy as np;
from sklearn.metrics import mean_absolute_error;
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf;
from statsmodels.tsa.ar_model import AutoReg;
from statsmodels.tsa.stattools import adfuller;
import pickle

def get_target(target_currency):

    collection = pd.read_csv("final_rates.csv")
    collection["Date"] = pd.to_datetime(collection["Date"])
    collection = collection.set_index("Date")
    
    print(collection.head())
    print(collection.tail())
    print(collection.shape)
    print(collection[target_currency].min())
    print(collection[target_currency].max())
    print(collection[target_currency].idxmin())
    
    """
    
    """
    lower_bound = 5
    upper_bound = 40
    collection = collection[(collection[target_currency] >= lower_bound) & (collection[target_currency] <= upper_bound)]
    
    print(collection.tail())
    print(collection.shape)
    print(collection[target_currency].min())
    print(collection[target_currency].max())
    print(collection[target_currency].idxmin())

    if target_currency in collection.columns:
        # Create a DataFrame with just the target currency

        try:
            target_df = collection[target_currency].dropna().astype(float).to_frame()
            #print(target_df.head())

        except:
            target_df = collection[target_currency].dropna().str.replace(",", "").astype(float).to_frame()
            
                
    
        """
        # Calculate the first and third quartiles
        lower_bound = target_df[target_currency].quantile(0.9)
        upper_bound = target_df[target_currency].quantile(0.1)
        iqr = upper_bound - lower_bound
        lower_bound = 0.90 
        upper_bound = 1.8 
        

        # Remove outliers
        lower_bound = 0.90 
        upper_bound = 1.8
        target_df = target_df[(target_df[target_currency] >= lower_bound) & (target_df[target_currency] <= upper_bound)]"""
       
        # Resample to weekly frequency and fill forward any missing values
        
        resampled_df = target_df.resample('W').mean().fillna(method='ffill')

        resampled_df = resampled_df.diff().dropna()
            
        return resampled_df
        
       

    
    else:

        print(f"Error: '{target_currency}' not found in columns: {collection.columns.tolist()}")
        return None
    



target = "ZMK"       

df = get_target(target)

print(df.head())
print(df.tail())

"""
#Different tests ran on data

#boxplot mainly for outliers
fig, ax = plt.subplots(figsize=(15, 6))
plt.boxplot(df)
plt.ylabel("Exchange Rate")
plt.title("Exchange Rate Boxplot")
plt.show()

#A simple line(time series) plot, shows the trend of the data
fig, ax = plt.subplots(figsize=(15, 6))
df[target].plot(ax=ax, xlabel = "time",ylabel = "Exhange Rate", title ="Exchange Rate time series")
plt.show()

#rolling mean shows wether or not the data had a constant mean(was stationary)
fig, ax = plt.subplots(figsize=(15, 6))
df[target].rolling(168).mean().plot(ax=ax,ylabel="Exchange Rate",title="weekly moving average")
plt.show() 

#partial autocorrelation function, shows the correlation of the data with itself and helps determine the number of lags to use
fig, ax = plt.subplots(figsize=(15, 6))
plot_pacf(df, ax=ax)
plt.xlabel("Lag [weeks]")
plt.ylabel("Correlation Coefficient")
plt.title("Autocorrelation Function")

#ADF test, tests for stationarity of the data
result = adfuller(df)
print('ADF Statistic: %f' % result[0])
print('p-value: %f' % result[1])
print('Critical Values:')
for key, value in result[4].items():
    print('\t%s: %.3f' % (key, value))
plt.show()
"""



#split the data into train and test sets
cutoff_test = int(len(df)*0.9)

df_train = df.iloc[:cutoff_test]
df_test = df.iloc[cutoff_test:]

df_train_mean = df_train.mean()
df_pred_baseline = [df_train_mean] * len(df_train)
mae_baseline = mean_absolute_error(df_train, df_pred_baseline)

print("Mean P2 Reading:", round(df_train_mean, 2))
print("Baseline MAE:", round(mae_baseline, 2))

model = AutoReg(df_train,lags=25, old_names=False).fit()

df_pred = model.predict().dropna()
training_mae = mean_absolute_error(df_train.iloc[25:],df_pred)
print("Training MAE:", training_mae)

df_pred_test = model.predict(df_test.index.min(), df_test.index.max())
test_mae = mean_absolute_error(df_pred_test, df_test)
print("Test MAE:", test_mae)

#save the model

model.save("model.pkl")
