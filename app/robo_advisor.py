
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
latest_day_str = datetime.strptime(latest_day,'%Y-%m-%d')
latest_day_date = latest_day_str.strftime('%B %d, %Y')
latest_close = tsd[latest_day]["4. close"]
latest_volume = tsd[latest_day]["5. volume"]

# recent high and low and volume
high_prices = []
low_prices = []
high_volumes = []
for d in tsd:
    high_price = float(tsd[d]["2. high"])
    low_price = float(tsd[d]["3. low"])
    high_volume = int(tsd[d]["5. volume"])
    high_prices.append(high_price)
    low_prices.append(low_price)
    high_volumes.append(high_volume)

recent_high = max(high_prices)
recent_low = min(high_prices)
recent_high_volume = max(high_volumes)


# get date for recent high and volume
for d in tsd:
    if float(tsd[d]["2. high"]) == recent_high:
        recent_high_date = d
        recent_high_datef = datetime.strptime(recent_high_date,'%Y-%m-%d').date()
        print(recent_high_datef)
    if float(tsd[d]["5. volume"]) == recent_high_volume:
        recent_high_volume_date = d




# RECOMMENDATION AND REASON

# if close price is > recent high and volume is > recent high volume, then BUY
if (float(latest_close) > float(recent_high)) and (int(latest_volume) > int(recent_high_volume)):
    latest_volume = "{:,}".format(int(latest_volume))
    recent_high_volume = "{:,}".format(int(recent_high_volume))
    recommendation = "BUY"
    reason = f"{stock.upper()}'s latest close of {to_usd(float(latest_close))} is greater than its recent high of {to_usd(float(recent_high))}, and its most recent volume of {latest_volume} is also greater than its recent high volume of {recent_high_volume}. This indicates that demand will likely continue pushing the price up."
elif (float(latest_close) > float(recent_high)) and (int(latest_volume) < int(recent_high_volume)):
    latest_volume = "{:,}".format(int(latest_volume))
    recent_high_volume = "{:,}".format(int(recent_high_volume))
    recommendation = "DON'T BUY"
    reason = f"{stock.upper()}'s latest close of {to_usd(float(latest_close))} is greater than its recent high of {to_usd(float(recent_high))}, but its most recent volume of {latest_volume} is not greater than its recent high volume of {recent_high_volume}. This indicates that it is likely not demand pushing the price up, and the price may not continue increasing."
elif (float(latest_close) < float(recent_high)) and (int(latest_volume) > int(recent_high_volume)):
    latest_volume = "{:,}".format(int(latest_volume))
    recent_high_volume = "{:,}".format(int(recent_high_volume))
    recommendation = "DON'T BUY"
    reason = f"Even though {stock.upper()}'s most recent volume of {latest_volume} is greater than its recent high volume of {recent_high_volume}, its latest close of {to_usd(float(latest_close))} is less than its recent high of {to_usd(float(recent_high))}."
elif (float(latest_close) < float(recent_high)) and (int(latest_volume) < int(recent_high_volume)):
    latest_volume = "{:,}".format(int(latest_volume))
    recent_high_volume = "{:,}".format(int(recent_high_volume))
    recommendation = "DON'T BUY"
    reason = f"{stock.upper()}'s latest close of {to_usd(float(latest_close))} is not greater than its recent high of {to_usd(float(recent_high))}, and its most recent volume of {latest_volume} is not greater than its recent high volume of {recent_high_volume}. This indicates that there is not much interest in this stock, and the price may not increase in the near future."



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


# DATA VIZ

line_data = []
for d in tsd:
    d_date = datetime.strptime(d,'%Y-%m-%d').date()
    entry = {"Date": d_date, "StockPrice": float(tsd[d]["4. close"])}
    line_data.append(entry)

line_data.reverse()
line_df = DataFrame(line_data)




# pass our dataframe to the charting function, specifying which attribute to chart
#plot = sns.lineplot(data=line_df,x="Date",y="Stock Price")

plt.plot(line_df.Date, line_df.StockPrice, label="Daily Close Price")
plt.ylabel("Stock Price ($)")
plt.xlabel("Date")
plt.axhline(y=float(recent_high), color='r', label=f"Recent High: {recent_high_datef}")
plt.legend(loc='lower left', bbox_to_anchor= (0.0, 1.01), ncol=2,
            borderaxespad=0, frameon=False)
plt.title(f"Plot of Prices for {stock.upper()}", y=1.07)
plt.savefig('prices.png')
plt.show()



print("-------------------------")
print(f"SELECTED SYMBOL: {stock.upper()}")
print("-------------------------")
print("REQUESTING STOCK MARKET DATA...")
print(f"REQUEST AT: {request_at_str}")
print("-------------------------")
print(f"LATEST DAY: {latest_day_date}")
print(f"LATEST CLOSE: {to_usd(float(latest_close))}")
print(f"RECENT HIGH: {to_usd(float(recent_high))}")
print(f"RECENT LOW: {to_usd(float(recent_low))}")
print("-------------------------")
print(f"RECOMMENDATION: {recommendation}")
print(f"RECOMMENDATION REASON: {reason}")
print("-------------------------")
print("WRITING TO CSV...")
print("-------------------------")
print("HAPPY INVESTING!")
print("-------------------------")