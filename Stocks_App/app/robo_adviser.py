import csv
from dotenv import load_dotenv
import json
import os
import pdb
import requests
import datetime

today = datetime.date.today()

#DEFINE TIME SERIES DATA
def parse_response(response_text):

    if isinstance(response_text, str):
        response_text = json.loads(response_text)

    results = []
    time_series_daily = response_text["Time Series (Daily)"]
    for trading_date in time_series_daily:
        prices = time_series_daily[trading_date]
        result = {
            "date": trading_date,
            "open": prices["1. open"],
            "high": prices["2. high"],
            "low": prices["3. low"],
            "close": prices["4. close"],
            "volume": prices["5. volume"]
        }
        results.append(result)
    return results

#DEFINE FUNCTION TO WRITE TO CSV WITH THE TIME SERIES DATA
def write_prices_to_file(prices=[], filename="db/prices.csv"):
    csv_filepath = os.path.join(os.path.dirname(__file__), "..", filename)
    with open(csv_filepath, "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["timestamp", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        for d in prices:
            row = {
                "timestamp": d["date"],
                "open": d["open"],
                "high": d["high"],
                "low": d["low"],
                "close": d["close"],
                "volume": d["volume"]
            }
            writer.writerow(row)


if __name__ == '__main__':

#READING API KEY SETUP IN THE .ENV FILE
    load_dotenv()

    api_key = os.environ.get("ALPHAVANTAGE_API_KEY") or "OOPS. Please set an environment variable named 'ALPHAVANTAGE_API_KEY'."

    # CAPTURE USER INPUTS (SYMBOL)
    symbol = input("Please input a stock symbol (e.g. 'NFLX'): ")

    # VALIDATE SYMBOL AND PREVENT UNECESSARY REQUESTS
try:
    float(symbol)
    quit("CHECK YOUR SYMBOL. EXPECTING NON-NUMERIC ENTRY")
except ValueError as e:

    # ASSEMBLE REQUEST URL
    request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"

    # ISSUE "GET" REQUEST
    response = requests.get(request_url)

    # VALIDATE RESPONSE AND HANDLE ERRORS
    if "Error Message" in response.text:
        print("REQUEST ERROR, PLEASE TRY AGAIN. CHECK YOUR STOCK SYMBOL")
        quit("Stopping THE PROGRAM")

    # PARSE RESPONSE
    daily_prices = parse_response(response.text)

    # WRITE TO CSV
    write_prices_to_file(prices=daily_prices, filename="db/prices.csv")


    # PERFORM CALCULATIONS
    # LAST CLOSING
    latest_price = daily_prices[0]["close"]
    latest_price = float(latest_price)
    latest_price_usd = "${0:,.2f}".format(latest_price)


    # AVERAGE HIGH
    recent_100_highs = [float(daily_price["high"]) for daily_price in daily_prices]
    average_recent_100_high = sum(recent_100_highs)/len(recent_100_highs)
    average_recent_100_high_usd = "${0:,.2f}".format(average_recent_100_high)


    # AVERAGE LOW
    recent_100_lows = [float(daily_price["low"]) for daily_price in daily_prices]
    average_recent_100_low = sum(recent_100_lows)/len(recent_100_lows)
    average_recent_100_low_usd = "${0:,.2f}".format(average_recent_100_low)


#WELCOME MENU
    menu = """
    ------------------------
    ROBO STOCK ADVISER
    ------------------------
    Welcome to the Robotic Stock Advisery Application

    This tool will display daily price information for the
    selected stock and provide you with a reccomended course
    of action.
    ------------------------
    """

#PRINT SEQUENCE (I tried to get this all in my menu so I could just print that but kept failing and ran out of time)
print(menu)
print("    " +"AS OF:" + " " + str(today))
print("    " + f"LATEST DAILY CLOSING FOR {symbol} IS: {latest_price_usd}")
print("    " + f"LATEST AVERAGE HIGH FOR {symbol} IS: {average_recent_100_high_usd}")
print("    " + f"LATEST AVERAGE LOW FOR {symbol} IS: {average_recent_100_low_usd}")
print("    " + "--------------------")

#RECCOMENDATION
if latest_price_usd > average_recent_100_high_usd:
   print("    " + "ROBO ADIVSER'S RECCOMENDATION IS TO SELL!")

if latest_price_usd < average_recent_100_low_usd:
    print("    " + "ROBO ADVISER'S RECCOMENDATION IS TO BUY!")

if average_recent_100_low_usd < latest_price_usd < average_recent_100_high_usd:
    print("    " + "ROBO ADVISESR'S RECCOMENDATION IS TO HOLD!")
print("    " + "---------------------")
