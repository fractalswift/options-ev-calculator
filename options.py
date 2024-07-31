import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from py_vollib.black_scholes import black_scholes as bs
from py_vollib.black_scholes.implied_volatility import implied_volatility

def generate_days_to_check(days_to_expiry):
    if days_to_expiry <= 30:  # For short-term options (1 month or less)
        return [0, 1, 3, 7, 14, 21, days_to_expiry]
    elif days_to_expiry <= 90:  # For medium-term options (1-3 months)
        return [0, 7, 14, 30, 60, days_to_expiry]
    elif days_to_expiry <= 365:  # For options up to 1 year
        return [0, 30, 90, 180, 270, days_to_expiry]
    else:  # For long-term options (more than 1 year)
        checkpoints = [0, 30, 90, 180, 365]
        while checkpoints[-1] < days_to_expiry - 365:
            checkpoints.append(checkpoints[-1] + 365)
        checkpoints.append(days_to_expiry)
        return checkpoints

def calculate_pnl(S, K, expiry_date, r, market_price, price_range, num_samples):
    today = datetime.now().date()
    days_to_expiry = (expiry_date - today).days
    t = days_to_expiry / 365.0
    
    impl_vol = implied_volatility(market_price, S, K, t, r, 'c')
    initial_value = bs('c', S, K, t, r, impl_vol)
    
    price_samples = np.linspace(price_range[0], price_range[1], num_samples)
    days_to_check = generate_days_to_check(days_to_expiry)
    
    results = []
    for new_S in price_samples:
        for days in days_to_check:
            future_date = today + timedelta(days=days)
            if future_date > expiry_date:
                continue
            
            new_t = max(0, (expiry_date - future_date).days / 365.0)
            new_value = bs('c', new_S, K, new_t, r, impl_vol)
            
            pnl = new_value - initial_value
            pnl_percentage = (pnl / market_price) * 100
            
            results.append({
                'Date': future_date,
                'Days_To_Expiry': (expiry_date - future_date).days,
                'Stock_Price': new_S,
                'Option_Value': new_value,
                'PnL_$': pnl,
                'PnL_%': pnl_percentage
            })
    
    return pd.DataFrame(results)

# Inputs
S = 231.06  # Current stock price
K = 520  # Strike price
expiry_date = datetime.strptime("16/01/26", "%d/%m/%y").date()  # Expiry date
r = 0.05  # Risk-free rate
market_price = 31.85  # Market price of the option

# Define scenarios
price_range = [200, 800]  # Range of stock prices to analyze
num_samples = 5  # Number of price samples to generate

# Calculate PnL for different scenarios
pnl_df = calculate_pnl(S, K, expiry_date, r, market_price, price_range, num_samples)

# Display results
pd.set_option('display.float_format', '{:.2f}'.format)
print(pnl_df.to_string(index=False))

# Optionally, save to CSV for easy spreadsheet import
pnl_df.to_csv('option_pnl_scenarios.csv', index=False)
print("\nResults saved to 'option_pnl_scenarios.csv'")