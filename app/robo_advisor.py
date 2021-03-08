
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

stocks = []
parsed_responses_daily = []
num_stocks = 0
symexists = 0

while True:
    stock = input("Please enter a stock or cryptocurrency symbol (type 'DONE' when finished, max 5 symbols): ")
    stock = stock.upper()
    if stock.lower() == "done":
        break

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

    for y in stocks:
        if y == stock:
            symexists = 1
        else:
            symexists = 0

    # data validate
    if len(stock) > 6:
        print("Hm, that doesn't look like a valid symbol. Please try again!")
        next
    elif stock.isnumeric() == True:
        print("Hm, that doesn't look like a valid symbol. Please try again!")
        next
    elif invalidsymbol == 1:
        print("Hm, that doesn't look like a valid symbol. Please try again!")
        next
    elif symexists == 1:
        print("You've already entered that symbol!")
        next
    elif num_stocks > 4:
        print("Sorry, we can only handle 5 stocks at a time. Please type 'DONE' to run analysis.")
    else:
        stocks.append(stock.upper())
        parsed_responses_daily.append(parsed_response)
        num_stocks += 1


# request at:
request_at = datetime.now()
request_at_f = request_at.strftime('%B %d, %Y %I:%M %p')

# create list of output dictionaries for each stock
outputs = []

for x in parsed_responses_daily:
    
    # symbol
    print(x)
    sym = x["Meta Data"]["2. Symbol"]

    # latest day
    tsd = x["Time Series (Daily)"]
    dates = list(tsd.keys())
    dates.sort(key=lambda date:datetime.strptime(date,"%Y-%m-%d"), reverse = True)
    latest_day = dates[0]
    latest_day_str = datetime.strptime(latest_day,'%Y-%m-%d')
    latest_day_date = latest_day_str.strftime('%B %d, %Y')

    # latest close 
    latest_close = float(tsd[latest_day]["4. close"])

    # recent high and low
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

    # volume
    yesterday = dates[1]
    latest_volume = int(tsd[latest_day]["5. volume"])
    yesterday_volume = int(tsd[yesterday]["5. volume"])
    yesterday_date = datetime.strptime(yesterday,'%Y-%m-%d').date()

    # recommendation/reason
    # if close price is > recent high and volume is > yesterday's volume, then BUY
    if (latest_close > recent_high) and (latest_volume > yesterday_volume):
        latest_volume = "{:,}".format(latest_volume)
        yesterday_volume = "{:,}".format(yesterday_volume)
        recommendation = "BUY"
        reason = f"{sym}'s latest close of {to_usd(latest_close)} is greater than its recent high of {to_usd(recent_high)}, and its most recent volume of {latest_volume} is also greater than its previous day volume of {yesterday_volume}. This indicates that demand will likely continue pushing the price up."
    elif (latest_close > recent_high) and (latest_volume <= yesterday_volume):
        latest_volume = "{:,}".format(latest_volume)
        yesterday_volume= "{:,}".format(yesterday_volume)
        recommendation = "DON'T BUY"
        reason = f"{sym}'s latest close of {to_usd(latest_close)} is greater than its recent high of {to_usd(recent_high)}, but its most recent volume of {latest_volume} is not greater than its previous day volume of {yesterday_volume}. This indicates that it is likely not demand pushing the price up, and the price may not continue increasing."
    elif (latest_close <= recent_high) and (latest_volume > yesterday_volume):
        latest_volume = "{:,}".format(latest_volume)
        yesterday_volume = "{:,}".format(yesterday_volume)
        recommendation = "DON'T BUY"
        reason = f"Even though {sym}'s most recent volume of {latest_volume} is greater than its previous day volume of {yesterday_volume}, its latest close of {to_usd(latest_close)} is not greater than its recent high of {to_usd(float(recent_high))}."
    elif (latest_close <= recent_high) and (latest_volume <= yesterday_volume):
        latest_volume = "{:,}".format(latest_volume)
        yesterday_volume = "{:,}".format(yesterday_volume)
        recommendation = "DON'T BUY"
        reason = f"{sym}'s latest close of {to_usd(latest_close)} is not greater than its recent high of {to_usd(recent_high)}, and its most recent volume of {latest_volume} is not greater than its previous day volume of {yesterday_volume}. This indicates that there is not much interest in this stock, and the price may not increase in the near future."


    
    stock_dict = {
        "Symbol": sym,
        "Request At": request_at_f,
        "Latest Day": latest_day_date,
        "Latest Close": to_usd(latest_close),
        "Recent High": to_usd(recent_high),
        "Recent Low": to_usd(recent_low),
        "Recommendation": recommendation,
        "Reason": reason,
    }

    outputs.append(stock_dict)
    
    # WRITE TO CSV

    csv_file_path = os.path.join(os.path.dirname(__file__),"..","data",f"prices_{sym}.csv")
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
summary = []

print("*************************")
print("*************************")
print(f"PRINTING RESULTS FOR: ")
for x in stocks:
    print(x)
print("*************************")
print("*************************")
for x in outputs:
    symbol_output = x["Symbol"]
    request_at_output = x["Request At"]
    latest_day_output = x["Latest Day"]
    latest_close_output = x["Latest Close"]
    recent_high_output = x["Recent High"]
    recent_low_output = x["Recent Low"]
    recommendation_output = x["Recommendation"]
    reason_output = x["Reason"]

    summary_dict = {
        "Symbol": symbol_output,
        "Recommendation": recommendation_output
    }
    summary.append(summary_dict)


    print(f"SELECTED SYMBOL: {symbol_output}")
    print("-------------------------")
    print("REQUESTING STOCK MARKET DATA...")
    print(f"REQUEST AT: {request_at_output}")
    print("-------------------------")
    print(f"LATEST DAY: {latest_day_output}")
    print(f"LATEST CLOSE: {latest_close_output}")
    print(f"RECENT HIGH: {recent_high_output}")
    print(f"RECENT LOW: {recent_low_output}")
    print("-------------------------")
    print(f"RECOMMENDATION: {recommendation_output}")
    print(f"RECOMMENDATION REASON: {reason_output}")
    print("*************************")
print("SUMMARY:")
for x in summary:
    sy = x["Symbol"]
    rec = x["Recommendation"]
    print(f"{sy}: {rec}")
print("*************************")
print("WRITING TO CSV...")
print("CREATING DATA VISUALIZATIONS...")
print("-------------------------")
print("HAPPY INVESTING!")
print("-------------------------")    


# DATA VIZ
count = 1
for x in parsed_responses_daily:
    
    # create data frame for prices
    line_data = []
    tsd = x["Time Series (Daily)"]
    for d in tsd:
        d_date = datetime.strptime(d,'%Y-%m-%d').date()
        entry = {"Date": d_date, "StockPrice": float(tsd[d]["4. close"])}
        line_data.append(entry)

    line_data.reverse()
    line_df = DataFrame(line_data)

    # get symbol
    sym = x["Meta Data"]["2. Symbol"]

    # get recent high and date
    high_prices = []
    for d in tsd:
        high_price = float(tsd[d]["2. high"])
        high_prices.append(high_price)

    recent_high = float(max(high_prices))

    # get date for recent high 
    for d in tsd:
        if float(tsd[d]["2. high"]) == recent_high:
            recent_high_date = d
            recent_high_datef = datetime.strptime(recent_high_date,'%Y-%m-%d').date()

    # plot price graph and recent high line
    plt.figure(count)
    plt.subplot(1,2,1)
    plt.plot(line_df.Date, line_df.StockPrice, label="Daily Close Price")
    plt.ylabel("Stock Price ($)")
    plt.xlabel("Date")
    plt.axhline(y=recent_high, color='r', label=f"Recent High: {recent_high_datef}")
    plt.legend(loc='lower left', bbox_to_anchor= (0.0, 1.01), ncol=2,
                borderaxespad=0, frameon=False)
    plt.title(f"Plot of Prices for {sym}", y=1.07)
    plt.savefig(f'visualizations/prices_{sym}.png')

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
    plt.subplot(1,2,2)
    plt.plot(volumeline_df.Date, volumeline_df.Volume, label="Daily Volume")
    plt.ylabel("Daily Volume (# Shares)")
    plt.xlabel("Date")
    plt.axhline(y=yesterday_volume, color='r', label=f"Previous Day's Volume: {yesterday_date}")
    plt.legend(loc='lower left', bbox_to_anchor= (0.0, 1.01), ncol=2,
                borderaxespad=0, frameon=False)
    plt.title(f"Plot of Daily Volume for {sym}", y=1.07)
    plt.savefig(f'visualizations/volumes_{sym}.png')

    count += 1

plt.show()