import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.stats import norm
from py_vollib.black_scholes import black_scholes as bs
from py_vollib.black_scholes.implied_volatility import implied_volatility

def generate_days_to_check(days_to_expiry):
    if days_to_expiry <= 30:
        return [0, 7, 14, days_to_expiry]
    elif days_to_expiry <= 90:
        return [0, 14, 30, days_to_expiry]
    elif days_to_expiry <= 365:
        return [0, 30, 90, days_to_expiry]
    else:
        checkpoints = [0, 90, 365]
        while checkpoints[-1] < days_to_expiry - 365:
            checkpoints.append(checkpoints[-1] + 365)
        checkpoints.append(days_to_expiry)
        return checkpoints[:4]  # Limit to 4 checkpoints

def calculate_probability(S, K, t, r, sigma):
    if t == 0:
        return 1 if S >= K else 0
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * t) / (sigma * np.sqrt(t))
    return norm.cdf(d1)

def calculate_pnl(S, K, expiry_date, r, market_price, price_range, num_samples):
    today = datetime.now().date()
    days_to_expiry = (expiry_date - today).days
    t = days_to_expiry / 365.0
    impl_vol = implied_volatility(market_price, S, K, t, r, 'c')
    initial_value = market_price
    price_samples = np.linspace(price_range[0], price_range[1], num_samples)
    days_to_check = generate_days_to_check(days_to_expiry)
    results = []

    print(f"Implied Volatility: {impl_vol}")  # Debugging output

    for new_S in price_samples:
        for days in days_to_check:
            future_date = today + timedelta(days=days)
            if future_date > expiry_date:
                continue
            new_t = max(0, (expiry_date - future_date).days / 365.0)
            time_to_future = days / 365.0
            new_value = bs('c', new_S, K, new_t, r, impl_vol)
            pnl = new_value - initial_value
            pnl_percentage = (pnl / market_price) * 100
            
            # Calculate probability of stock being above the current price at the future date
            prob_above = calculate_probability(S, new_S, time_to_future, r, impl_vol)
            prob_below = 1 - prob_above
            
            # Calculate EV considering both profit scenario and loss scenario
            ev_percentage = pnl_percentage * prob_above + (-100 * prob_below)
            
            results.append({
                'Date': future_date,
                'Days_To_Expiry': (expiry_date - future_date).days,
                'Stock_Price': new_S,
                'Option_Value': new_value,
                'PnL_$': pnl,
                'PnL_%': pnl_percentage,
                'Prob_Above': prob_above,
                'Prob_Below': prob_below,
                'EV_%': ev_percentage
            })

            # Debugging output
            if new_S == 800:
                print(f"Date: {future_date}, Probability for S>={new_S}: {prob_above}")
                print(f"PnL for S={new_S}: {pnl}")
                print(f"EV% for S={new_S}: {ev_percentage}")

    print(f"Maximum EV%: {max(result['EV_%'] for result in results)}")
    print(f"Minimum EV%: {min(result['EV_%'] for result in results)}")

    return pd.DataFrame(results)

# Inputs
S = 231.06  # Current stock price
K = 520  # Strike price
expiry_date = datetime.strptime("16/01/26", "%d/%m/%y").date()  # Expiry date
r = 0.05  # Risk-free rate
market_price = 31.85  # Market price of the option

# Define scenarios
price_range = [200, 800]  # Range of stock prices to analyze
num_samples = 20  # Number of price samples to generate

# Calculate PnL for different scenarios
pnl_df = calculate_pnl(S, K, expiry_date, r, market_price, price_range, num_samples)

# Display results
pd.set_option('display.float_format', '{:.4f}'.format)
print(pnl_df.to_string(index=False))

# Optionally, save to CSV for easy spreadsheet import
pnl_df.to_csv('option_pnl_scenarios.csv', index=False)
print("\nResults saved to 'option_pnl_scenarios.csv'")

# Calculate and display overall Expected Value
overall_ev_percent = pnl_df['EV_%'].mean()
print(f"\nOverall Expected Value: {overall_ev_percent:.2f}%")