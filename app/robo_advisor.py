
import requests
import json
import os
import csv
import pandas as pd
import seaborn as sns
from pandas import DataFrame

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from datetime import datetime
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

    if len(parsed_response) == 0:
        invalidsymbol = 1


    print(parsed_response)
    print("here")
    print(invalidsymbol)
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
request_at_str = request_at.strftime('%B %d, %Y %I:%M %p')

# latest day and close
tsd = parsed_response["Time Series (Daily)"]
dates = list(tsd.keys())
dates.sort(key=lambda date:datetime.strptime(date,"%Y-%m-%d"), reverse = True)

latest_day = dates[0]
yesterday = dates[1]
latest_day_str = datetime.strptime(latest_day,'%Y-%m-%d')
latest_day_date = latest_day_str.strftime('%B %d, %Y')
latest_close = float(tsd[latest_day]["4. close"])
latest_volume = int(tsd[latest_day]["5. volume"])

# recent high and low and volume
high_prices = []
low_prices = []
for d in tsd:
    high_price = float(tsd[d]["2. high"])
    low_price = float(tsd[d]["3. low"])
    high_prices.append(high_price)
    low_prices.append(low_price)

recent_high = float(max(high_prices))
recent_low = float(min(high_prices))



# get date for recent high 
for d in tsd:
    if float(tsd[d]["2. high"]) == recent_high:
        recent_high_date = d
        recent_high_datef = datetime.strptime(recent_high_date,'%Y-%m-%d').date()
    

# get yesterday's volume
yesterday_volume = int(tsd[yesterday]["5. volume"])
yesterday_date = datetime.strptime(yesterday,'%Y-%m-%d').date()


# RECOMMENDATION AND REASON

# if close price is > recent high and volume is > yesterday's volume, then BUY
if (latest_close > recent_high) and (latest_volume > yesterday_volume):
    latest_volume = "{:,}".format(latest_volume)
    yesterday_volume = "{:,}".format(yesterday_volume)
    recommendation = "BUY"
    reason = f"{stock.upper()}'s latest close of {to_usd(latest_close)} is greater than its recent high of {to_usd(recent_high)}, and its most recent volume of {latest_volume} is also greater than its previous day volume of {yesterday_volume}. This indicates that demand will likely continue pushing the price up."
elif (latest_close > recent_high) and (latest_volume <= yesterday_volume):
    latest_volume = "{:,}".format(latest_volume)
    yesterday_volume= "{:,}".format(yesterday_volume)
    recommendation = "DON'T BUY"
    reason = f"{stock.upper()}'s latest close of {to_usd(latest_close)} is greater than its recent high of {to_usd(recent_high)}, but its most recent volume of {latest_volume} is not greater than its previous day volume of {yesterday_volume}. This indicates that it is likely not demand pushing the price up, and the price may not continue increasing."
elif (latest_close <= recent_high) and (latest_volume > yesterday_volume):
    latest_volume = "{:,}".format(latest_volume)
    yesterday_volume = "{:,}".format(yesterday_volume)
    recommendation = "DON'T BUY"
    reason = f"Even though {stock.upper()}'s most recent volume of {latest_volume} is greater than its previous day volume of {yesterday_volume}, its latest close of {to_usd(latest_close)} is not greater than its recent high of {to_usd(float(recent_high))}."
elif (latest_close <= recent_high) and (latest_volume <= yesterday_volume):
    latest_volume = "{:,}".format(latest_volume)
    yesterday_volume = "{:,}".format(yesterday_volume)
    recommendation = "DON'T BUY"
    reason = f"{stock.upper()}'s latest close of {to_usd(latest_close)} is not greater than its recent high of {to_usd(recent_high)}, and its most recent volume of {latest_volume} is not greater than its previous day volume of {yesterday_volume}. This indicates that there is not much interest in this stock, and the price may not increase in the near future."


# WRITE TO CSV
csv_file_path = os.path.join(os.path.dirname(__file__),"..","data","stockprices.csv")
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


# OUTPUT

print("-------------------------")
print(f"SELECTED SYMBOL: {stock.upper()}")
print("-------------------------")
print("REQUESTING STOCK MARKET DATA...")
print(f"REQUEST AT: {request_at_str}")
print("-------------------------")
print(f"LATEST DAY: {latest_day_date}")
print(f"LATEST CLOSE: {to_usd(latest_close)}")
print(f"RECENT HIGH: {to_usd(recent_high)}")
print(f"RECENT LOW: {to_usd(recent_low)}")
print("-------------------------")
print(f"RECOMMENDATION: {recommendation}")
print(f"RECOMMENDATION REASON: {reason}")
print("-------------------------")
print("WRITING TO CSV...")
print("CREATING DATA VISUALIZATIONS...")
print("-------------------------")
print("HAPPY INVESTING!")
print("-------------------------")

# DATA VIZ

# create data frame for prices
line_data = []
for d in tsd:
    d_date = datetime.strptime(d,'%Y-%m-%d').date()
    entry = {"Date": d_date, "StockPrice": float(tsd[d]["4. close"])}
    line_data.append(entry)

line_data.reverse()
line_df = DataFrame(line_data)

# plot price graph and recent high line
plt.figure(1)
plt.plot(line_df.Date, line_df.StockPrice, label="Daily Close Price")
plt.ylabel("Stock Price ($)")
plt.xlabel("Date")
plt.axhline(y=recent_high, color='r', label=f"Recent High: {recent_high_datef}")
plt.legend(loc='lower left', bbox_to_anchor= (0.0, 1.01), ncol=2,
            borderaxespad=0, frameon=False)
plt.title(f"Plot of Prices for {stock.upper()}", y=1.07)
plt.savefig('visualizations/prices.png')

# create data frame for volume
volumeline_data = []
for d in tsd:
    d_date2 = datetime.strptime(d,'%Y-%m-%d').date()
    entry = {"Date": d_date2, "Volume": int(tsd[d]["5. volume"])}
    volumeline_data.append(entry)

volumeline_data.reverse()
volumeline_df = DataFrame(volumeline_data)
yesterday_volume = int(tsd[yesterday]["5. volume"])

# plot volume graph and recent high volume line
plt.figure(2)
plt.plot(volumeline_df.Date, volumeline_df.Volume, label="Daily Volume")
plt.ylabel("Daily Volume (# Shares)")
plt.xlabel("Date")
plt.axhline(y=yesterday_volume, color='r', label=f"Previous Day's Volume: {yesterday_date}")
plt.legend(loc='lower left', bbox_to_anchor= (0.0, 1.01), ncol=2,
            borderaxespad=0, frameon=False)
plt.title(f"Plot of Daily Volume for {stock.upper()}", y=1.07)
plt.savefig('visualizations/volumes.png')
plt.show()