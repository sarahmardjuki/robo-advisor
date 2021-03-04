
from datetime import datetime
import requests
import json
import os
import csv
from dotenv import load_dotenv

load_dotenv() # load contents of .env file to environment

# functions
def to_usd(my_price):
    return "${0:,.2f}".format(my_price)

# INPUTS
api_key = os.environ.get("ALPHAVANTAGE_API_KEY")

# USER INPUT
while True:
    stock = input("Please enter a stock or cryptocurrency symbol: ")

    request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock}&apikey={api_key}"

    response = requests.get(request_url)
    parsed_response = json.loads(response.text)
    for key, value in parsed_response.items():
        if key == "Error Message":
            invalidsymbol = 1
            break 
        else:
            invalidsymbol = 0

    # data validate
    if len(stock) > 6:
        print("Hm, that doesn't look like a valid symbol. Please try again!")
    elif stock.isnumeric() == True:
        print("Hm, that doesn't look like a valid symbol. Please try again!")
    elif invalidsymbol == 1:
        print("Hm, that doesn't look like a valid symbol. Please try again!")
    else:
        break





# request at:
request_at = datetime.now()
request_at_str = request_at.strftime('%Y-%m-%d %I:%M %p')

# latest day and close
tsd = parsed_response["Time Series (Daily)"]
dates = list(tsd.keys())
dates.sort(key=lambda date:datetime.strptime(date,"%Y-%m-%d"), reverse = True)

latest_day = dates[0]
latest_close = tsd[latest_day]["4. close"]

# recent high and low


high_prices = []
low_prices = []
for d in tsd:
    high_price = tsd[d]["2. high"]
    low_price = tsd[d]["3. low"]
    high_prices.append(high_price)
    low_prices.append(low_price)

recent_high = max(high_prices)
recent_low = min(high_prices)


# WRITE TO CSV
csv_file_path = os.path.join(os.path.dirname(__file__),"..","data","prices.csv")
with open(csv_file_path, "w") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=["timestamp", "open", "high", "low", "close", "volume"])
    writer.writeheader()
    for d in tsd:
        writer.writerow({
            "timestamp": d,
            "open": tsd[d]["1. open"],
            "high": tsd[d]["2. high"],
            "low": tsd[d]["3. low"],
            "close": tsd[d]["4. close"],
            "volume": tsd[d]["5. volume"],
        })



print("-------------------------")
print(f"SELECTED SYMBOL: {stock}")
print("-------------------------")
print("REQUESTING STOCK MARKET DATA...")
print(f"REQUEST AT: {request_at_str}")
print("-------------------------")
print(f"LATEST DAY: {latest_day}")
print(f"LATEST CLOSE: {to_usd(float(latest_close))}")
print(f"RECENT HIGH: {to_usd(float(recent_high))}")
print(f"RECENT LOW: {to_usd(float(recent_low))}")
print("-------------------------")
print(f"RECOMMENDATION: ")
print(f"RECOMMENDATION REASON: ")
print("-------------------------")
print("WRITING TO CSV...")
print("-------------------------")
print("HAPPY INVESTING!")
print("-------------------------")