def calculate_investment_ev(max_gain_percent, chance_of_max, chance_of_zero):
    # Convert percentages to decimals
    max_gain = max_gain_percent / 100
    
    # Calculate expected value
    ev = (max_gain * chance_of_max) - (1 * chance_of_zero)
    
    # Convert to percentage
    ev_percent = ev * 100
    
    return ev_percent

# Example usage
max_gain_percent = 500  # 500% max gain
chance_of_max = 0.1  # 10% chance of reaching max
chance_of_zero = 0.3  # 30% chance of losing everything

result = calculate_investment_ev(max_gain_percent, chance_of_max, chance_of_zero)
print(f"The expected value is: {result:.2f}%")