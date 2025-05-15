import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle
from dateutil.relativedelta import relativedelta

def predict_exchange_rate(target_date, model_path="model.pkl", data_path="final_rates.csv", target_currency="ZWL"):
    """
    Predict the exchange rate for a given target date using the saved AutoReg model.
    
    Parameters:
    -----------
    target_date : str or datetime
        The date for which to predict the exchange rate. If str, format should be 'YYYY-MM-DD'.
    model_path : str, default="model.pkl"
        Path to the saved model file.
    data_path : str, default="final_rates.csv"
        Path to the CSV file containing the historical exchange rate data.
    target_currency : str, default="ZWL"
        The currency code for which to predict the exchange rate.
        
    Returns:
    --------
    float
        Predicted exchange rate for the target date.
    """
    
    if isinstance(target_date, str):
        target_date = pd.to_datetime(target_date)
    
    
    if not isinstance(target_date, datetime):
        raise ValueError("target_date must be a datetime object or a date string in format 'YYYY-MM-DD'")
    
    # Load the model
    try:
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Model file not found at {model_path}")
    
    # Load and preprocess the historical data
    collection = pd.read_csv(data_path)
    collection["Date"] = pd.to_datetime(collection["Date"])
    collection = collection.set_index("Date")
    
    if target_currency not in collection.columns:
        raise ValueError(f"Currency '{target_currency}' not found in the dataset.")
    
    # Create a DataFrame with just the target currency
    try:
        target_df = collection[target_currency].dropna().astype(float).to_frame()
    except:
        target_df = collection[target_currency].dropna().str.replace(",", "").astype(float).to_frame()
    
    # Remove outliers
    lower_bound = target_df[target_currency].quantile(0.1)
    upper_bound = target_df[target_currency].quantile(0.9)

    #Used the above quartiles because the data is not normally distributed
    iqr = upper_bound - lower_bound
    lower_bound = lower_bound - 1.5 * iqr
    upper_bound = upper_bound + 1.5 * iqr
    target_df = target_df[(target_df[target_currency] >= lower_bound) & 
                          (target_df[target_currency] <= upper_bound)]
    
    # Resample to weekly frequency and fill forward any missing values
    resampled_df = target_df.resample('W').mean().fillna(method='ffill')
    original_resampled_df = resampled_df.copy() 

    # Create differenced data to make the data more stationary
    resampled_df = resampled_df.diff().dropna()  
    
    
    latest_date = resampled_df.index.max()
    
    #for any dates after the 8th of April 2024, we need to divide by the exchange rate of ZIG to RTGS
    
    if target_date <= latest_date:
        
        # The target date is within our historical data, so we can just return it
        if target_date in resampled_df.index:
            
            return (original_resampled_df.loc[target_date, target_currency]/2498.7242
                    if target_date >= datetime.strptime("08 April 2024", '%d %B %Y')
                    else original_resampled_df.loc[target_date, target_currency])
        else:

            # Find the nearest date in our dataset
            nearest_date = original_resampled_df.index[original_resampled_df.index.get_indexer([target_date], method='nearest')[0]]
            
            return (original_resampled_df.loc[nearest_date, target_currency]/2498.7242
                    if nearest_date >= datetime.strptime("08 April 2024", '%d %B %Y')
                    else original_resampled_df.loc[nearest_date, target_currency])
    
    # For future dates beyond our data, use the model to forecast
    
    #account for the train/test split
    cutoff_test = int(len(resampled_df)*0.9)
    last_date_in_model = resampled_df.index[cutoff_test-1]

    #print(f"Last date in model: {type(last_date_in_model)}")

    
    # Determine how many weeks ahead we need to forecast
    weeks_ahead = (target_date - last_date_in_model).days // 7 + 1
    
    
    # Determine how far in the past the model goes for each prediction
    lag_order = 25  # Default value
    if hasattr(model, 'ar_lags'):
        lag_order = max(model.ar_lags) if model.ar_lags else 25
    elif hasattr(model, 'k_ar'):
        lag_order = model.k_ar
    
   
    # Use the model's forecast method directly
    forecast_result = [i for i in model.forecast(steps=weeks_ahead)]
        
    # Create a date range for the forecast period
    forecast_dates = pd.date_range(start=last_date_in_model + pd.Timedelta(days=7), 
                                  periods=weeks_ahead, 
                                  freq='W')
    
    
    # Create forecast DataFrame
    forecast_df = pd.DataFrame(forecast_result, index=forecast_dates, columns=[target_currency])
    #print(f"Forecast DataFrame: {forecast_df}")

    # Find the closest date to our target in the forecast
    closest_date = forecast_df.index[forecast_df.index.get_indexer([target_date], method='nearest')[0]]
    #print(f"Closest date in forecast: {closest_date}")

    # Get the last actual (non-differenced) value
    last_actual = original_resampled_df.iloc[-1, 0]
    #print(f"Last actual value: {last_actual}")

    # Calculate the cumulative sum of differences for each forecast date
    forecast_df['cumulative_diff'] = forecast_df[target_currency].cumsum()
    

    target_cum_diff = forecast_df.loc[closest_date, 'cumulative_diff']
    #print(target_cum_diff)

    final_prediction = last_actual + target_cum_diff
    #print(final_prediction)

    # Ensure prediction is not negative (exchange rates are typically positive)
    final_prediction = max(0.0001, final_prediction)
    
    return (float(final_prediction)/2498.7242 
            if target_date >= datetime.strptime("08 April 2024", '%d %B %Y') 
            else float(final_prediction))

print(predict_exchange_rate("2025-05-01"))  # Example usage
