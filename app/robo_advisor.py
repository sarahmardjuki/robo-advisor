
import requests
import json
import os
import csv
import pandas as pd
from pandas import DataFrame

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

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
parsed_responses_weekly = []
num_stocks = 0
symexists = 0

while True:
    stock = input("Please enter a stock or cryptocurrency symbol (type 'DONE' when finished, max 5 symbols): ")
    stock = stock.upper()
    if stock.lower() == "done":
        break

    # preliminary data validation
    if len(stock) > 6:
        print("Hm, that doesn't look like a valid symbol. Please try again!")
        next
    elif stock.isnumeric() == True:
        print("Hm, that doesn't look like a valid symbol. Please try again!")
        next
    else:    
        request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={stock}&apikey={api_key}"

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
        if invalidsymbol == 1:
            print("Hm, that doesn't look like a valid symbol. Please try again!")
            next
        elif symexists == 1:
            print("You've already entered that symbol!")
            next
        elif num_stocks > 4:
            print("Sorry, we can only handle 5 stocks at a time. Please type 'DONE' to run analysis.")
        else:
            stocks.append(stock.upper())
            parsed_responses_weekly.append(parsed_response)
            num_stocks += 1


# request at:
request_at = datetime.now()
request_at_f = request_at.strftime('%B %d, %Y %I:%M %p')

# create list of output dictionaries for each stock
outputs = []

for x in parsed_responses_weekly:
    # symbol
    sym = x["Meta Data"]["2. Symbol"]

    # latest day
    tsw = x["Weekly Time Series"]
    dates = list(tsw.keys())
    dates.sort(key=lambda date:datetime.strptime(date,"%Y-%m-%d"), reverse = True)
    latest_day = dates[0]
    latest_day_str = datetime.strptime(latest_day,'%Y-%m-%d')
    latest_day_date = latest_day_str.strftime('%B %d, %Y')

    # latest close 
    latest_close = float(tsw[latest_day]["4. close"])

    # 52 wk high and low
    high_prices = []
    low_prices = []
    iter = 1
    for d in tsw:
        if iter <= 52:
            high_price = float(tsw[d]["2. high"])
            low_price = float(tsw[d]["3. low"])
            high_prices.append(high_price)
            low_prices.append(low_price)
            iter += 1
        else:
            break

    ftweek_high = float(max(high_prices))
    ftweek_low = float(min(low_prices))

    # get date for 52wk high 
    iter = 1
    for d in tsw:
        if iter <= 52:
            if float(tsw[d]["2. high"]) == ftweek_high:
                ftweek_high_date = d
                ftweek_high_datef = datetime.strptime(ftweek_high_date,'%Y-%m-%d').date()
        else:
            break

    # volume and last week volume
    lastwk = dates[1]
    latest_volume = int(tsw[latest_day]["5. volume"])
    lastwk_volume = int(tsw[lastwk]["5. volume"])
    lastwk_date = datetime.strptime(lastwk,'%Y-%m-%d').date()

    # last week high
    lastwk_high = float(tsw[lastwk]["2. high"])

    # recommendation/reason
    # if close price is > last week's high and volume is > last week's volume, then BUY, otherwise DON'T BUY
    if (latest_close > lastwk_high) and (latest_volume > lastwk_volume):
        latest_volume = "{:,}".format(latest_volume)
        lastwk_volume = "{:,}".format(lastwk_volume)
        recommendation = "BUY"
        reason = f"{sym}'s latest close of {to_usd(latest_close)} is greater than last week's high of {to_usd(lastwk_high)}, and its most recent volume of {latest_volume} shares is also greater than last week's volume of {lastwk_volume} shares. This indicates that demand will likely continue pushing the price up."
    elif (latest_close > lastwk_high) and (latest_volume <= lastwk_volume):
        latest_volume = "{:,}".format(latest_volume)
        lastwk_volume= "{:,}".format(lastwk_volume)
        recommendation = "DON'T BUY"
        reason = f"{sym}'s latest close of {to_usd(latest_close)} is greater than last week's high of {to_usd(lastwk_high)}, but its most recent volume of {latest_volume} shares is not greater than last week's volume of {lastwk_volume} shares. This indicates that it is likely not demand pushing the price up, and the price may not continue increasing."
    elif (latest_close <= lastwk_high) and (latest_volume > lastwk_volume):
        latest_volume = "{:,}".format(latest_volume)
        lastwk_volume = "{:,}".format(lastwk_volume)
        recommendation = "DON'T BUY"
        reason = f"Even though {sym}'s most recent volume of {latest_volume} shares is greater than last week's volume of {lastwk_volume} shares, its latest close of {to_usd(latest_close)} is not greater than last week's high of {to_usd(lastwk_high)}."
    elif (latest_close <= lastwk_high) and (latest_volume <= lastwk_volume):
        latest_volume = "{:,}".format(latest_volume)
        lastwk_volume = "{:,}".format(lastwk_volume)
        recommendation = "DON'T BUY"
        reason = f"{sym}'s latest close of {to_usd(latest_close)} is not greater than last week's high of {to_usd(lastwk_high)}, and its most recent volume of {latest_volume} shares is not greater than last week's volume of {lastwk_volume} shares. This indicates that there is not much interest in this stock, and the price may not increase in the near future."


    
    stock_dict = {
        "Symbol": sym,
        "Request At": request_at_f,
        "Latest Day": latest_day_date,
        "Latest Close": to_usd(latest_close),
        "52 Wk High": to_usd(ftweek_high),
        "52 Wk Low": to_usd(ftweek_low),
        "Recommendation": recommendation,
        "Reason": reason,
    }

    outputs.append(stock_dict)
    
    # WRITE TO CSV

    csv_file_path = os.path.join(os.path.dirname(__file__),"..","data",f"prices_{sym}.csv")
    with open(csv_file_path, "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["timestamp", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        for d in tsw:
            writer.writerow({
                "timestamp": d,
                "open": tsw[d]["1. open"],
                "high": tsw[d]["2. high"],
                "low": tsw[d]["3. low"],
                "close": tsw[d]["4. close"],
                "volume": tsw[d]["5. volume"],
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
    ftwk_high_output = x["52 Wk High"]
    ftwk_low_output = x["52 Wk Low"]
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
    print(f"52 WK HIGH: {ftwk_high_output}")
    print(f"52 WK LOW: {ftwk_low_output}")
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
for x in parsed_responses_weekly:
    
    # create data frame for prices
    line_data = []
    tsw = x["Weekly Time Series"]
    iterate = 1
    for d in tsw:
        if iterate <= 52:
            d_date = datetime.strptime(d,'%Y-%m-%d').date()
            entry = {"Date": d_date, "StockPrice": float(tsw[d]["4. close"])}
            line_data.append(entry)
            iterate += 1
        else:
            break

    line_data.reverse()
    line_df = DataFrame(line_data)

    # get symbol
    sym = x["Meta Data"]["2. Symbol"]

    # get last week's high and date
    dates = list(tsw.keys())
    dates.sort(key=lambda date:datetime.strptime(date,"%Y-%m-%d"), reverse = True)
    lastwk = dates[1]
    lastwk_date = datetime.strptime(lastwk,'%Y-%m-%d').date()
    lastwk_high = float(tsw[lastwk]["2. high"])


    # plot price graph and last week's high line
    plt.figure(count,figsize=(12,5))
    plt.subplot(1,2,1)
    plt.plot(line_df.Date, line_df.StockPrice, label="Weekly Close Price")
    plt.ylabel("Stock Price ($)")
    plt.xlabel("Date")
    plt.axhline(y=lastwk_high, color='r', label=f"Last Week's High ({lastwk_date})")
    plt.legend(loc='lower left', bbox_to_anchor= (0.0, 1.01), ncol=2,
                borderaxespad=0, frameon=False)
    plt.title(f"Plot of Weekly Prices for {sym}", y=1.07)

    # create data frame for volume
    volumeline_data = []
    iterate = 1
    for d in tsw:
        if iterate <= 52:
            d_date2 = datetime.strptime(d,'%Y-%m-%d').date()
            entry = {"Date": d_date2, "Volume": int(tsw[d]["5. volume"])}
            volumeline_data.append(entry)
            iterate += 1
        else:
            break

    volumeline_data.reverse()
    volumeline_df = DataFrame(volumeline_data)
    lastwk_volume = int(tsw[lastwk]["5. volume"])

    # plot volume graph and 52 wk high volume line
    plt.subplot(1,2,2)
    plt.plot(volumeline_df.Date, volumeline_df.Volume, label="Weekly Volume")
    plt.ylabel("Weekly Volume (# Shares)")
    plt.xlabel("Date")
    plt.axhline(y=lastwk_volume, color='r', label=f"Last Week's Volume ({lastwk_date})")
    plt.legend(loc='lower left', bbox_to_anchor= (0.0, 1.01), ncol=2,
                borderaxespad=0, frameon=False)
    plt.title(f"Plot of Weekly Volume for {sym}", y=1.07)
    plt.savefig(f'visualizations/pricesandvolumes_{sym}.png')

    count += 1

plt.show()