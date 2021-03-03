

import requests
import json

# functions
def to_usd(my_price):
    return "${0:,.2f}".format(my_price)

# USER INPUT
while True:
    stock = input("Please enter a stock or cryptocurrency symbol: ")

    # data validate
    if len(stock) > 6:
        print("Hm, that doesn't look like a valid symbol. Please try again!")
    elif stock.isnumeric() == True:
        print("Hm, that doesn't look like a valid symbol. Please try again!")
    else:
        break

request_url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&apikey=demo"

response = requests.get(request_url)
parsed_response = json.loads(response.text)
latest_day = parsed_response["Meta Data"]["3. Last Refreshed"]
latest_close = parsed_response["Time Series (Daily)"][latest_day]["4. close"]

tsd = parsed_response["Time Series (Daily)"]
high_prices = []
low_prices = []
for d in tsd:
    high_price = tsd[d]["2. high"]
    low_price = tsd[d]["3. low"]
    high_prices.append(high_price)
    low_prices.append(low_price)

recent_high = max(high_prices)
recent_low = min(high_prices)

print("-------------------------")
print(f"SELECTED SYMBOL: {stock}")
print("-------------------------")
print("REQUESTING STOCK MARKET DATA...")
print(f"REQUEST AT: ")
print("-------------------------")
print(f"LATEST DAY: {latest_day}")
print(f"LATEST CLOSE: {to_usd(float(latest_close))}")
print(f"RECENT HIGH: {to_usd(float(recent_high))}")
print(f"RECENT LOW: {to_usd(float(recent_low))}")
print("-------------------------")
print(f"RECOMMENDATION: ")
print(f"RECOMMENDATION REASON: ")
print("-------------------------")
print("HAPPY INVESTING!")
print("-------------------------")