import yfinance as yf

def fetch_options(ticker):
    # Fetch the ticker object
    stock = yf.Ticker(ticker)
    
    # Get the available expirations
    expirations = stock.options
    
    # Collect all available options data
    options_data = []
    for expiry in expirations:
        opt_chain = stock.option_chain(expiry)
        
        # Collect calls data
        for call in opt_chain.calls.itertuples():
            option_data = {
                'symbol': call.contractSymbol,
                'expiry': expiry,
                'strike': call.strike,
                'right': 'C',
                'askPrice': call.ask
            }
            options_data.append(option_data)
        
        # Collect puts data
        for put in opt_chain.puts.itertuples():
            option_data = {
                'symbol': put.contractSymbol,
                'expiry': expiry,
                'strike': put.strike,
                'right': 'P',
                'askPrice': put.ask
            }
            options_data.append(option_data)
    
    return options_data

# Example usage
ticker = 'COIN'
options_data = fetch_options(ticker)

# Print results
for option in options_data:
    print(option)
