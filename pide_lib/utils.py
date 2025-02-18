from binance.enums import HistoricalKlinesType
from binance.client import Client
from threading import Thread
import ccxt
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import csv
import os
import time
import json
import configparser
import logging
import warnings
import sys

# Add the directory containing the bot package to the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
# Get the absolute path to the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

# Add the parent directory to the Python path if it's not already there
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


# Define a function to handle warnings
def handle_warnings(message, category, filename, lineno, file=None, line=None):
    pass


# Attach the custom warning handler
warnings.showwarning = handle_warnings

# Redirect warnings to sys.stderr (or any other file)
warnings.simplefilter("ignore", category=UserWarning)
warnings.simplefilter("ignore", category=FutureWarning)
# Suppress warnings
warnings.filterwarnings("ignore")
# Filter out the warnings you want to suppress
warnings.filterwarnings(
    "ignore", message="No runtime found, using MemoryCacheStorageManager")

# Configure logging
logging.basicConfig(level=logging.ERROR)


def set_config_settings(config_file_path, sandbox_mode, trading_type='spot'):

    # Create a ConfigParser object
    config = configparser.ConfigParser()
    config.read(config_file_path)

    # Update the sandbox mode in the configuration
    config.set('Settings', 'sandbox_mode', str(sandbox_mode))
    config.set('Settings', 'trading_type', trading_type.capitalize())

    # Write the updated configuration back to the file
    with open(config_file_path, 'w') as config_file:
        config.write(config_file)

    print("Sandbox mode updated successfully.")


def set_api_key_secret(api_key, secret_key, config_file_path, trading_type, live_mode=False):
    # Create a ConfigParser object
    config = configparser.ConfigParser()
    config.read(config_file_path)

    # Choose the appropriate section based on the trading_type
    section = 'FuturesKeys' if trading_type.lower() == 'futures' else 'SpotKeys'

    # Update the API key and secret based on live_mode
    sub_section_key = 'livekeys' if live_mode else 'demokeys'
    sub_section_secret = 'live_secret' if live_mode else 'demo_secret'
    config[section][sub_section_key] = api_key
    config[section][sub_section_secret] = secret_key

    # Write the updated configuration to the file
    with open(config_file_path, 'w') as config_file:
        config.write(config_file)

    print("API Key and Secret saved successfully.")


def get_api_credentials(config_file_path, mode_choice, trading_type):
    # st.write(f"Config file path: {config_file_path}")
    # Create a ConfigParser object
    config = configparser.ConfigParser()
    config.read(config_file_path)

    # Choose the appropriate section based on the trading_type
    section = 'FuturesKeys' if trading_type.lower() == 'futures' else 'SpotKeys'

    # Fetch the API key and secret
    api_key = config[section]['demokeys'] if mode_choice == 'Sandbox/Demo' else config[section]['livekeys']
    secret = config[section]['demo_secret'] if mode_choice == 'Sandbox/Demo' else config[section]['live_secret']
    # st.write(f"API Key fetched inside function: {api_key}")
    # st.write(f"Secret Key fetched inside function: {secret}")
    return api_key, secret


def get_mode(config_file_path):
    # Create a ConfigParser object
    config = configparser.ConfigParser()
    config.read(config_file_path)
    # print(config.sections())
    # Get the value of sandbox_mode from the Settings section
    sandbox_mode = config.getboolean("Settings", "sandbox_mode")
    print("Sandbox mode:", sandbox_mode)
    if sandbox_mode:
        return "Sandbox/Demo"
    else:
        return "Live"


# def check_authentication(exchange):
#     try:
#         balance = exchange.fetch_balance()  # Replace with an actual API request
#         # If the request succeeds, the authentication is correct
#         return True

#     except ccxt.AuthenticationError as e:
#         # Handle authentication errors
#         return False

#     except ccxt.NetworkError as e:
#         # Handle network errors
#         return False

#     except Exception as e:
#         # Handle other exceptions
#         return False


# @st.cache_resource
# def krakenActive(mode_choice, trading_type, config_file_path):
#     try:
#         # Set sandbox mode based on the selected mode
#         if mode_choice == "Sandbox/Demo":
#             sandbox_mode = True
#         else:
#             sandbox_mode = False

#         api_key, secret_key = get_api_credentials(
#             config_file_path, mode_choice, trading_type)
#         # st.write(f"API Key outside function: {api_key}")
#         # st.write(f"Secret Key outside function: {secret_key}")
#         # sandbox_mode = mode_choice == "Sandbox/Demo"
#         # Configure the exchange based on trading type
#         if trading_type.lower() == "spot":
#             exchange_class = ccxt.kraken
#         elif trading_type.lower() == "futures":
#             exchange_class = ccxt.krakenfutures
#         else:
#             raise ValueError("Invalid trading type. Use 'spot' or 'futures'.")

#         exchange = exchange_class(
#             {
#                 "apiKey": api_key,
#                 "secret": secret_key,
#                 "verbose": False,  # switch it to False if you don't want the HTTP log
#             }
#         )

#         # Enable or disable sandbox mode based on the selected mode
#         exchange.set_sandbox_mode(sandbox_mode)

#         # Check if the API key and secret are authenticated
#         if check_authentication(exchange):
#             # Authentication successful
#             _message = "Authentication Successful"
#             print(_message)  # Print the error to the console
#             return exchange
#         else:
#             # Authentication failed
#             e_message = "Authentication failed due to invalid key or secret."
#             print(e_message)  # Print the error to the console
#             return None
#     except Exception as e:
#         print(f"Error during activation: {e}")
#         return None
    # finally:
    #     # Ensure that exchange resources are closed, even if an exception occurs
    #     close_exchange(exchange)

# Function to check authentication and display messages





def serverTime(exchange):
    try:
        # Attempt to fetch time from the exchange
        time = exchange.fetch_time()
        time = pd.to_datetime(time, unit="ms")
        # print(f"Exchange Server Time: {time}")
        return time
    except ccxt.NotSupported:
        # Fallback to local system time if fetch_time() is not supported
        local_time = datetime.now()
        # print(f"Local System Time (fallback): {local_time}")
        return local_time


# def print_prominent_time(time):
#     # Convert the datetime object to a string before passing to pyfiglet
#     time_str = time.strftime("%Y-%m-%d %H:%M:%S")
#     # Convert time string to ASCII art
#     figlet_text = pyfiglet.figlet_format(time_str)
#     # Print in prominent style with color
#     print(colored(figlet_text, 'cyan', attrs=['bold']))


def print_prominent_time_in_box(time):
    # Convert the datetime object to a string
    time_str = time.strftime("%Y-%m-%d %H:%M:%S")

    # Define the box structure
    border = "+" + "-" * (len(time_str) + 2) + "+"
    content = f"| {time_str} |"

    # Print the time in a box
    print(border)
    print(content)
    print(border)


def get_position_quantity(exchange, symbol):
    try:
        # Fetch positions
        pos_info = exchange.fetchPositions(symbol)

        # Extract position quantity
        quantity = pos_info[0]["info"]['size']

        return quantity

    except ccxt.BaseError as e:
        print("An error occurred:", e)
        return None  # Return None in case of an error


def getqty(exchange, coin):
    params = {'type': 'futures'}
    for item in exchange.fetch_balance(params=params)['info']['balances']:
        if item['asset'] == coin:
            qty = float(item['free'])
    return qty


def place_buy_order(exchange, symbol, size):
    try:
        buyId = exchange.create_market_buy_order(symbol, size, params={})
        return buyId
    except:
        return False


# Define function to place sell order
def place_sell_order(exchange, symbol, size):
    # try:
    sellId = exchange.create_market_sell_order(symbol, size)
    return sellId
    # except:
    #     return False


def calculate_order_size(exchange, symbol, usdt_amount):
    # Get the current market price of the coin
    ticker = exchange.fetch_ticker(symbol)
    price = ticker['last']
    # Calculate the order size based on the USDT amount and the market price
    size = usdt_amount / price
    print(size)
    amount = round(size, 3)  # Round to 8 decimal places

    print('Order Size:', amount)

    return amount


# { ==========================================================================================
# Load historical price data from kraken exchange, but data is limited to 720 candles
# kraken = ccxt.kraken()

# Dictionary to store minimum periods for different timeframes
tf_min_period = {
    '1min': 1,
    '5min': 5,
    '15min': 15,
    '30min': 30,
    '1hour': 60,
    '4hour': 240,
    '12hour': 720,
    '1day': 1440,  # Assuming 1 day = 1440 minutes
    '1week': 10080  # Assuming 1 week = 10080 minutes
}

# Function to calculate the start date based on the selected end date and timeframe


def calculate_start_date(end_date, timeframe):
    # Get the minimum period for the selected timeframe
    min_period = tf_min_period.get(timeframe, None)
    if min_period is None:
        raise ValueError("Invalid timeframe selected")

    # Calculate the start date by subtracting the minimum period multiplied by 100
    start_date = end_date - timedelta(minutes=min_period * 100)

    return start_date


def start_time(kraken, ticker, days, trading_type="spot"):
    # Assume fetch_ticker is a function that fetches ticker data
    if trading_type == "spot":
        # Getting current timestamp
        timestamp = kraken.fetch_time()
        print(
            f'Current Time of kraken {trading_type}: {pd.to_datetime(timestamp, unit="ms")}')
        start_timestamp = timestamp - days * 86400 * 1000  # Calculating start timestamp
        start_time = pd.to_datetime(start_timestamp, unit='ms')
        return start_timestamp
    else:
        # Assume fetch_ticker is a function that fetches ticker data
        ticker_data = kraken.fetch_ticker(ticker)
        # Extracting timestamp from ticker data
        timestamp = ticker_data['timestamp']
        print(
            f"Current Time of kraken {trading_type}: {pd.to_datetime(timestamp, unit='ms')}")
        return None


# @st.cache_data
def getdata_kraken(kraken, symbol, timeframe, days, trading_type="spot"):
    try:
        df = pd.DataFrame(kraken.fetch_ohlcv(
            symbol, timeframe, since=start_time(kraken, symbol, days, trading_type.lower())))
        # print(df)
        df = df[[0, 1, 2, 3, 4, 5]]
        df.columns = ['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
        df = df.set_index('timestamp')
        # Convert the datetime index to date+hh:mm:ss format
        df.index = pd.to_datetime(df.index, unit='ms')
        df = df.astype(float)
        return df
    except Exception as e:
        # Handle the exception (you can customize this based on your requirements)
        print(f"An error occurred: {e}")
        return None


# Apply the cache decorator only if Streamlit is available
if 'streamlit' in globals():
    st.cache_data(getdata_kraken)
# }============================================================================================


# Load historical price data from binance exchange
binance = Client()


def get_futures_ohlcv(ticker, timeframe, day):
    try:
        start_str = f"{int(timeframe[:-1]) * day * 3600}m"
        df = pd.DataFrame(binance.futures_historical_klines(
            ticker, timeframe, start_str))
        df = df[[0, 1, 2, 3, 4, 5]]
        df.columns = ['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
        df = df.set_index('timestamp')
        # Convert the datetime index to date+hh:mm:ss format
        df.index = pd.to_datetime(df.index, unit='ms')
        df = df.astype(float)
        return df
    except Exception as e:
        # Handle the exception (you can customize this based on your requirements)
        print(f"An error occurred: {e}")
        return None


if 'streamlit' in globals():
    st.cache_data(get_futures_ohlcv)

# @st.cache_data()


def get_futures_data(ticker, interval, contract_type):
    # Fetch continuous futures klines based on the contract type
    r = binance.futures_continous_klines(
        pair=ticker,
        contractType=contract_type,  # Use 'PERPETUAL', 'CURRENT_MONTH', etc.
        interval=interval,
    )

    # Convert the raw response to a DataFrame
    df = pd.DataFrame(
        r,
        columns=[
            "timestamp",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "Close_time",
            "Quote_asset_volume",
            "Number_of_trades",
            "Taker_buy_base_asset_volume",
            "Taker_buy_quote_asset_volume",
            "Ignore",
        ],
    )

    # Set the 'timestamp' as the index and convert it to datetime
    df.set_index("timestamp", inplace=True)
    df.index = pd.to_datetime(df.index, unit="ms")

    # Convert necessary columns to numeric types
    df = df.apply(pd.to_numeric, errors="ignore")

    # Return only the desired columns: ["Open", "High", "Low", "Close", "Volume"]
    return df[["Open", "High", "Low", "Close", "Volume"]]


def getData(ticker, interval, start_str, end_str, trading_type):
    # st.write(f"ticker: {ticker}, interval: {interval}, start_str: {start_str}, end_str: {end_str}, trading_type: {trading_type}")
    trading_type_mapping = {
        "futures": HistoricalKlinesType.FUTURES,
        "spot": HistoricalKlinesType.SPOT
    }

    klines_type = trading_type_mapping.get(trading_type)
    print(f"Klines type: {klines_type}")

    if klines_type is None:
        raise ValueError("Invalid trading type")
    # Fetch historical klines from Binance based on the trading type
    if trading_type == "futures":
        print("Fetching futures data...")
        klines_type = HistoricalKlinesType.FUTURES  # Set the correct type directly
        klines = binance.get_historical_klines(
            symbol=ticker,
            interval=interval,
            start_str=start_str,
            end_str=end_str,
            klines_type=klines_type
        )
    else:
        print("Fetching spot data...")
        # Use Binance spot API method for spot data
        klines = binance.get_historical_klines(
            symbol=ticker,
            interval=interval,
            start_str=start_str,
            end_str=end_str,
            klines_type=klines_type,
        )

    # Convert the fetched data to a DataFrame
    df = pd.DataFrame(
        klines,
        columns=[
            "timestamp",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "Close_time",
            "Quote_asset_volume",
            "Number_of_trades",
            "Taker_buy_base_asset_volume",
            "Taker_buy_quote_asset_volume",
            "Ignore",
        ],
    )

    # Set the 'timestamp' as the index
    df.set_index("timestamp", inplace=True)
    # Convert the 'timestamp' index to datetime
    df.index = pd.to_datetime(df.index, unit="ms")
    # Convert columns to numeric (ignore 'timestamp' column)
    df = df.apply(pd.to_numeric, errors="ignore")

    return df[["Open", "High", "Low", "Close", "Volume"]]


if "streamlit" in globals():
    st.cache_data(getData)
# code for appending a new row to the trades CSV file

def in_pos(exchange, coin):
    balance = exchange.fetch_balance()['info']['balances']
    try:
        asset = float([i['free'] for i in balance if i['asset'] == coin][0])
        if asset > 0:
            in_position = True
        else:
            in_position = False
    except Exception as e:
        print(e)
        in_position = False
        asset = 0
    return in_position, balance, asset


def read_json_file(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading '{file_path}': {e}")
        return None


def st_icon(icon_name, color=None):
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">', unsafe_allow_html=True)
    classes = f"fas fa-{icon_name}"
    if color:
        icon_html = f'<i class="{classes} text-{color}"></i>'
    else:
        icon_html = f'<i class="{classes}"></i>'
    return icon_html


def save_parameters(params_dict):
    # Display input field for parameter name
    param_name = st.text_input("Enter a name for the parameters:")

    # Check if the save button is clicked
    if st.button("Save Optimized Parameters", key="save_parameters_click"):
        # Check if the parameter name is provided
        if param_name.strip():
            # Create the 'Results' folder if it doesn't exist
            if not os.path.exists("Results"):
                os.makedirs("Results")
            # Construct the filename
            filename = f"Results/{param_name.strip()}.json"
            try:
                # Save parameters to the file
                with open(filename, "w") as f:
                    json.dump(params_dict, f)
                st.success(f"Parameters saved with name: {param_name}")
            except Exception as e:
                st.error(f"Error occurred while saving parameters: {e}")
        else:
            st.warning("Please enter a name for the parameters.")


# Define the map_timeframe function (you've already provided this)
def setup_cronjob(tf, botorder_data_file, log_order_data_file):
    timeframe = map_timeframe(tf, get_value=True)
    st.write(f"Selected timeframe: {timeframe}")
    # Define the path to the bot script based on botorder_data_file
    bot_script_path = f"/home/ubuntu/myApp2/myenv/bin/python /home/ubuntu/myApp2/bot/{botorder_data_file}"

    # Define the log file path based on log_order_data_file
    log_file_path = f"/home/ubuntu/{log_order_data_file}"

    # Define the new cronjob command based on the selected timeframe and botorder_data_file
    new_cron_command = ""
    if timeframe == "1m":
        new_cron_command = f"*/1 * * * * {bot_script_path} >> {log_file_path} 2>&1"
    elif timeframe == "5m":
        new_cron_command = f"*/5 * * * * {bot_script_path} >> {log_file_path} 2>&1"
    elif timeframe == "15m":
        new_cron_command = f"*/15 * * * * {bot_script_path} >> {log_file_path} 2>&1"
    elif timeframe == "30m":
        new_cron_command = f"*/30 * * * * {bot_script_path} >> {log_file_path} 2>&1"
    elif timeframe == "1h":
        new_cron_command = f"0 * * * * {bot_script_path} >> {log_file_path} 2>&1"
    elif timeframe == "4h":
        new_cron_command = f"0 */4 * * * {bot_script_path} >> {log_file_path} 2>&1"
    elif timeframe == "6h":
        new_cron_command = f"0 */6 * * * {bot_script_path} >> {log_file_path} 2>&1"
    elif timeframe == "12h":
        new_cron_command = f"0 */12 * * * {bot_script_path} >> {log_file_path} 2>&1"
    elif timeframe == "1d":
        new_cron_command = f"0 0 * * * {bot_script_path} >> {log_file_path} 2>&1"
    elif timeframe == "1w":
        new_cron_command = f"0 0 * * 0 {bot_script_path} >> {log_file_path} 2>&1"
    else:
        st.write(f"Invalid timeframe: {timeframe}")
        return
    st.write(f"New cronjob command: {new_cron_command}")
    # Get the current user's cronjob by running the crontab command and save it to a temporary file
    os.system("crontab -l > temp_cronjob.txt")
    # Read the content of the temporary file
    with open("temp_cronjob.txt", "r") as file:
        lines = file.readlines()

    # Check if the existing cronjob command is found
    existing_cronjob_found = False
    for i, line in enumerate(lines):
        if bot_script_path in line:
            existing_cronjob_found = True
            # Replace the existing cronjob with the new cronjob command
            lines[i] = f"{new_cron_command}\n"
            st.write(
                f"Existing cronjob replaced with new command: {new_cron_command}")
            break
    # If the existing cronjob command is not found, append the new cronjob command to the end of the temporary file
    if not existing_cronjob_found:
        lines.append(f"{new_cron_command}\n")
        st.write(f"New cronjob added: {new_cron_command}")
    # st.write(f"Lines: {lines}")++++++++++++++++

    # Write the modified content back to the temporary file
    with open("temp_cronjob.txt", "w") as file:
        file.writelines(lines)

    # Use the crontab command to update the cronjobs from the temporary file
    result = os.system("crontab temp_cronjob.txt")
    # Remove the temporary file
    os.remove("temp_cronjob.txt")

    # Check the result and return a message accordingly
    if result == 0:
        return f"Cronjob updated successfully for {timeframe} timeframe and bot {botorder_data_file}."
    else:
        error_message = f"Failed to update cronjob. Error code: {result}"
        return error_message


def map_timeframe(resolution, get_value=True):
    tf_mapping = {
        '1min': '1m',
        '2min': '2m',
        '3min': '3m',
        '5min': '5m',
        '15min': '15m',
        '30min': '30m',
        '45min': '45m',
        '1hour': '1h',
        '4hour': '4h',
        '6hour': '6h',
        '12hour': '12h',
        '1day': '1d',
        '1week': '1w'
    }

    if get_value:
        return tf_mapping.get(resolution, '1d')  # Default to '1d' if not found
    else:
        # If you want to reverse map from value to resolution, you can do this:
        reverse_mapping = {v: k for k, v in tf_mapping.items()}
        # Default to '1day' if not found
        return reverse_mapping.get(resolution, '1day')


symbol_mapping = {
    "SANDUSDT": "SAND/USD:USD",
    "BTCUSDT": "BTC/USD:USD",
    "GALAUSDT": "GALA/USD:USD",
    "TUSDT": "TUSD/USD:USD",
    "AXSUSDT": "AXS/USD:USD",
    "CTKUSDT": "CTK/USD:USD",
    "SPELLUSDT": "SPELL/USD:USD",
    "EOSUSDT": "EOS/USD:USD",
    "AGIXUSDT": "AGIX/USD:USD",
    "DYDXUSDT": "DYDX/USD:USD",
    "LUNA2USDT": "LUNA2/USD:USD",
    "RENUSDT": "REN/USD:USD",
    "APEUSDT": "APE/USD:USD",
    "CHRUSDT": "CHR/USD:USD",
    "FLMUSDT": "FLM/USD:USD",
    "BTCDOMUSDT": "BTC/USD:USD-241227",
    "LDOUSDT": "LDO/USD:USD",
    "ZILUSDT": "ZIL/USD:USD",
    "OMGUSDT": "OMG/USD:USD",
    "1000XECUSDT": "XEC/USD:USD",
    "SOLUSDT": "SOL/USD:USD",
    "LINAUSDT": "LINA/USD:USD",
    "SFPUSDT": "SFP/USD:USD",
    "PEOPLEUSDT": "PEOPLE/USD:USD",
    "VETUSDT": "VET/USD:USD",
    "BAKEUSDT": "BAKE/USD:USD",
    "MINAUSDT": "MINA/USD:USD",
    "STORJUSDT": "STORJ/USD:USD",
    "HIGHUSDT": "HIGH/USD:USD",
    "RSRUSDT": "RSR/USD:USD",
    "YFIUSDT": "YFI/USD:USD",
    "MAGICUSDT": "MAGIC/USD:USD",
    "IDEXUSDT": "IDEX/USD:USD",
    "LQTYUSDT": "LQTY/USD:USD",
    "DOTUSDT": "DOT/USD:USD",
    "ASTRUSDT": "ASTR/USD:USD",
    "XEMUSDT": "XEM/USD:USD",
    "UMAUSDT": "UMA/USD:USD",
    "IOTAUSDT": "IOTA/USD:USD",
    "LINKUSDT": "LINK/USD:USD",
    "ALICEUSDT": "ALICE/USD:USD",
    "WOOUSDT": "WOO/USD:USD",
    "ETCUSDT": "ETC/USD:USD",
    "DUSKUSDT": "DUSK/USD:USD",
    "SKLUSDT": "SKL/USD:USD",
    "ENJUSDT": "ENJ/USD:USD",
    "HOOKUSDT": "HOOK/USD:USD",
    "ARKMUSDT": "ARKM/USD:USD",
    "NKNUSDT": "NKN/USD:USD",
    "XVGUSDT": "XVG/USD:USD",
    "COCOSUSDT": "COCOS/USD:USD",
    "HOTUSDT": "HOT/USD:USD",
    "LEVERUSDT": "LEVER/USD:USD",
    "MDTUSDT": "MDT/USD:USD",
    "ZECUSDT": "ZEC/USD:USD",
    "KAVAUSDT": "KAVA/USD:USD",
    "1000SHIBUSDT": "SHIB/USD:USD",
    "PHBUSDT": "PHB/USD:USD",
    "OCEANUSDT": "OCEAN/USD:USD",
    "TOMOUSDT": "TOMO/USD:USD",
    "ICXUSDT": "ICX/USD:USD",
    "FETUSDT": "FET/USD:USD",
    "MATICUSDT": "MATIC/USD:USD",
    "BALUSDT": "BAL/USD:USD",
    "IOSTUSDT": "IOST/USD:USD",
    "THETAUSDT": "THETA/USD:USD",
    "XRPUSDT": "XRP/USD:USD",
    "RADUSDT": "RAD/USD:USD",
    "CELOUSDT": "CELO/USD:USD",
    "1000PEPEUSDT": "PEPE/USD:USD",
    "API3USDT": "API3/USD:USD",
    "DOGEUSDT": "DOGE/USD:USD",
    "AVAXUSDT": "AVAX/USD:USD",
    "HFTUSDT": "HFT/USD:USD",
    "ZRXUSDT": "ZRX/USD:USD",
    "CFXUSDT": "CFX/USD:USD",
    "BLURUSDT": "BLUR/USD:USD",
    "ARBUSDT": "ARB/USD:USD",
    "WAVESUSDT": "WAVES/USD:USD",
    "UNFIUSDT": "UNFI/USD:USD",
    "LRCUSDT": "LRC/USD:USD",
    "TRBUSDT": "TRB/USD:USD",
    "SSVUSDT": "SSV/USD:USD",
    "IOTXUSDT": "IOTX/USD:USD",
    "MASKUSDT": "MASK/USD:USD",
    "ARPAUSDT": "ARPA/USD:USD",
    "ANTUSDT": "ANT/USD:USD",
    "HBARUSDT": "HBAR/USD:USD",
    "SNXUSDT": "SNX/USD:USD",
    "USDCUSDT": "USDC/USD:USD",
    "ENSUSDT": "ENS/USD:USD",
    "SUSHIUSDT": "SUSHI/USD:USD",
    "STXUSDT": "STX/USD:USD",
    "1INCHUSDT": "1INCH/USD:USD",
    "ATOMUSDT": "ATOM/USD:USD",
    "GRTUSDT": "GRT/USD:USD",
    "AMBUSDT": "AMB/USD:USD",
    "1000FLOKIUSDT": "FLOKI/USD:USD",
    "ALGOUSDT": "ALGO/USD:USD",
    "IMXUSDT": "IMX/USD:USD",
    "BANDUSDT": "BAND/USD:USD",
    "RNDRUSDT": "RNDR/USD:USD",
    "FLOWUSDT": "FLOW/USD:USD",
    "FOOTBALLUSDT": "FOOTBALL/USD:USD",
    "BCHUSDT": "BCH/USD:USD",
    "NEOUSDT": "NEO/USD:USD",
    "REEFUSDT": "REEF/USD:USD",
    "ARUSDT": "AR/USD:USD",
    "DARUSDT": "DAR/USD:USD",
    "BELUSDT": "BEL/USD:USD",
    "DASHUSDT": "DASH/USD:USD",
    "MKRUSDT": "MKR/USD:USD",
    "BLUEBIRDUSDT": "BLUEBIRD/USD:USD",
    "DENTUSDT": "DENT/USD:USD",
    "ATAUSDT": "ATA/USD:USD",
    "C98USDT": "C98/USD:USD",
    "GMTUSDT": "GMT/USD:USD",
    "LTCUSDT": "LTC/USD:USD",
    "INJUSDT": "INJ/USD:USD",
    "RDNTUSDT": "RDNT/USD:USD",
    "OPUSDT": "OP/USD:USD",
    "ZENUSDT": "ZEN/USD:USD",
    "GMXUSDT": "GMX/USD:USD",
    "JOEUSDT": "JOE/USD:USD",
    "QNTUSDT": "QNT/USD:USD",
    "COMBOUSDT": "COMBO/USD:USD",
    "BNXUSDT": "BNX/USD:USD",
    "WLDUSDT": "WLD/USD:USD",
    "XVSUSDT": "XVS/USD:USD",
    "DEFIUSDT": "DEFI/USD:USD",
    "KSMUSDT": "KSM/USD:USD",
    "SXPUSDT": "SXP/USD:USD",
    "CRVUSDT": "CRV/USD:USD",
    "AGLDUSDT": "AGLD/USD:USD",
    "XLMUSDT": "XLM/USD:USD",
    "CVXUSDT": "CVX/USD:USD",
    "FILUSDT": "FIL/USD:USD",
    "RLCUSDT": "RLC/USD:USD",
    "ALPHAUSDT": "ALPHA/USD:USD",
    "AAVEUSDT": "AAVE/USD:USD",
    "RUNEUSDT": "RUNE/USD:USD",
    "ANKRUSDT": "ANKR/USD:USD",
    "KEYUSDT": "KEY/USD:USD",
    "XTZUSDT": "XTZ/USD:USD",
    "MANAUSDT": "MANA/USD:USD",
    "QTUMUSDT": "QTUM/USD:USD",
    "PENDLEUSDT": "PENDLE/USD:USD",
    "FLUXUSDT": "FLUX/USD:USD",
    "TWTUSDT": "TWT/USD:USD",
    "TAROTUSDT": "TAROT/USD:USD",
    "YGGUSDT": "YGG/USD:USD",
    "STGUSDT": "STG/USD:USD",
    "TLMUSDT": "TLM/USD:USD",
    "MTLUSDT": "MTL/USD:USD",
    "UNIUSDT": "UNI/USD:USD",
    "LUNAUSDT": "LUNA/USD:USD",
    "ETHUSDT": "ETH/USD:USD",
    "BNBUSDT": "BNB/USD:USD",
    "TRXUSDT": "TRX/USD:USD",
    "ADAUSDT": "ADA/USD:USD",
    "NEARUSDT": "NEAR/USD:USD",
    "COMPUSDT": "COMP/USD:USD",
    "ICPUSDT": "ICP/USD:USD",
    "FTMUSDT": "FTM/USD:USD",
    "TAOUSDT": "TAO/USD:USD",
    "POPCATUSDT": "POPCAT/USD:USD",
    "BONKUSDT": "BONK/USD:USD"
}


def get_symbol_leverage_info(exchange, symbol_mapping):
    """
    Retrieves symbol and leverage information from the exchange and maps symbols
    using the provided symbol_mapping dictionary.

    Parameters:
        exchange (Exchange): The exchange object to fetch leverage information from.
        symbol_mapping (dict): A dictionary mapping symbols to their corresponding values.

    Returns:
        DataFrame: A DataFrame containing symbol and leverage information.
    """
    try:
        # Fetch leverage information from the exchange
        leverage_info = exchange.fetchLeverages()

        # Extract symbol and leverage information
        symbol_leverage_data = []
        for symbol, data in leverage_info.items():
            # Check if symbol exists in symbol_mapping values
            for key, value in symbol_mapping.items():
                if value == symbol:
                    symbol = key  # Replace symbol with the key from symbol_mapping
                    break
            leverage_with_suffix = str(data['longLeverage']) + 'x'
            symbol_leverage_data.append(
                {'Symbol': symbol, 'Leverage': leverage_with_suffix})

        # Create DataFrame
        df = pd.DataFrame(symbol_leverage_data)

        return df

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Function to convert Kraken symbols back to Binance format
def convert_kraken_to_binance(symbol):
    # Remove the `/USD:USD` part and add `USDT` to the base coin
    return symbol.split("/")[0] + "USDT"


def convert_symbol_format(user_symbol):
    base, quote = user_symbol[:-4], user_symbol[-4:-1]
    print(f"Base: {base}, Quote: {quote}")
    if base == "BTC":
        base = "XBT"
    return f"PF_{base}{quote}"


def set_leverage_for_symbols(exchange, leverage, symbols=None):
    if symbols is None:
        market_info = exchange.load_markets()
        symbols_list = [market_info[key]['id'] for key in market_info]
    else:
        symbols_list = symbols

    results = []
    for symbol in symbols_list:
        if symbol.startswith("PF"):  # Check if symbol starts with "PF"
            try:
                result = exchange.setLeverage(leverage, symbol)
                result_message = f"Leverage set successfully for symbol {symbol} to {leverage}: {result}"
                results.append({"symbol": symbol, "result": result_message})
                print(result_message)
                st.info(result_message)
            except Exception as e:
                error_message = f"Error setting leverage for symbol {symbol}: {e}"
                results.append({"symbol": symbol, "error": error_message})
                print(error_message)
                st.error(error_message)
        else:
            st.warning(
                f"Ignoring symbol {symbol} as it does not start with 'PF'.")
            print(f"Ignoring symbol {symbol} as it does not start with 'PF'.")

    return results


def calculate_balance(exchange, currency_code, percentage=0.20):
    try:
        # Fetch the balance from the exchange
        balance = exchange.fetch_balance()
        # Extract the free balance for the specified currency
        free_balance = balance[currency_code]['free']
        # Calculate the amount to use (20% of free balance)
        amount_to_use = free_balance * percentage
        # Extract the BTC free balance
        btc_free_balance = balance['BTC']['free']
        # Return the results
        return amount_to_use, free_balance, btc_free_balance

    except (KeyError, ccxt.BaseError) as e:
        # Handle errors, such as currency code not found or exchange fetch_balance error
        print(f"An error occurred: {e}")
        return None, None, None


def monitor_order_status(exchange, symbol, order_id, original_amount):
    try:
        while True:
            # Fetch recent trades
            trades = exchange.fetch_my_trades(
                symbol=symbol)  # Adjust symbol as needed

            # Initialize total filled amount
            total_filled = 0.0

            # Check if any trade corresponds to the order ID
            for trade in trades:
                if trade['order'] == order_id:
                    # Add the trade amount to the total filled amount
                    total_filled += trade['amount']

            # Check if the total filled amount matches the original order amount
            if total_filled >= original_amount:
                print("Order fully filled.")
                return

            # Wait for some time before checking again
            time.sleep(5)  # Adjust the sleep time as needed
    except Exception as e:
        print(f"Error while monitoring order status: {e}")


# def handle_insufficient_funds_error(exchange, symbol, timeframe, amount, tp_perc, stop_loss, order_type, position_type, state, max_retries=2):
#     retries = 0
#     response = None
#     returned_pos_info = None
#     while retries < max_retries:
#         # Reduce position size by 0.9 for each attempt (including the first attempt)
#         amount *= 0.9

#         # Retry placing the order
#         response, returned_pos_info, state = place_order_to_open_position(
#             exchange=exchange,
#             symbol=symbol,
#             timeframe=timeframe,
#             amount=amount,
#             tp_perc=tp_perc,
#             stop_loss=stop_loss,
#             order_type=order_type,
#             position_type=position_type,
#             state=state
#         )
#         if response is not None:
#             # Order placed successfully, exit the loop
#             break
#         else:
#             # Order placement failed, increment the retry count and try again
#             retries += 1
#             print(f"Retrying order placement. Attempt {retries}/{max_retries}")

#     if response is None:
#         print(f"Failed to place order after {max_retries} attempts.")
#         # You can handle this failure case as needed

#     return response, returned_pos_info, state


# def place_order_to_open_position(
#     exchange,
#     symbol,
#     timeframe,
#     amount,
#     tp_perc,
#     sl_price,
#     order_type,
#     position_type,
#     state=None,
#     trades_directory=None,
# ):
#     # Assign the module-level `trades_directory` if not provided
#     if trades_directory is None:
#         trades_directory = globals().get('trades_directory', "trades")

#     print(f"Placing {order_type} order for {amount} {symbol} at market price")
#     print(f"Position Type: {position_type}")
#     print(f"TP perc: {tp_perc}")
#     print(f"SL price: {sl_price}")

#     # Get file paths for the order book, trades, and position info
#     order_data_file, trade_file, pos_file, _, _ = get_file_paths(symbol, trades_directory)

#     try:
#         if position_type == "long":
#             response = exchange.create_market_buy_order(symbol=symbol, amount=amount)
#         else:
#             response = exchange.create_market_sell_order(symbol=symbol, amount=amount)
#         time.sleep(5)

#         if response is None or not response:
#             print("Failed to place order. Response is None or empty.")
#             return None

#         print(response)
#         if "info" in response and "order_id" in response["info"]:
#             order_id = response["info"]["order_id"]
#             price = None
#             side = response["side"]

#             # Extract entry time from response
#             entry_time_str = response["info"].get("receivedTime", None)
#             if entry_time_str:
#                 entry_time = datetime.strptime(
#                     entry_time_str, "%Y-%m-%dT%H:%M:%S.%fZ"
#                 ).strftime("%Y-%m-%d %H:%M:%S")
#             else:
#                 entry_time = None

#             if "orderEvents" in response["info"]:
#                 order_events = response["info"]["orderEvents"]
#                 for event in order_events:
#                     if "type" in event and event["type"] == "EXECUTION":
#                         price = float(event["price"])
#                         break

#             if price is None:
#                 print("Failed to get price from response. Price is None.")
#                 return None

#             Thread(
#                 target=monitor_order_status, args=(exchange, symbol, order_id, amount)
#             ).start()

#             total_filled = 0.0
#             try:
#                 if "orderEvents" in response["info"]:
#                     for event in response["info"]["orderEvents"]:
#                         if event["type"] == "EXECUTION":
#                             total_filled += float(event["amount"])

#                     order_qty = round(total_filled, 4)
#                     status = response["info"]["status"]
#                     print("Order status:", status)
#                     print("Total filled amount:", order_qty)
#                 else:
#                     order_qty = round(float(response["amount"]), 4)
#             except KeyError as e:
#                 print(f"An error occurred while processing order events: {e}")
#                 return None, None, None

#             in_position = True
#             limit = None
#             status = "open"

#             if position_type == "long":
#                 tp_price = price * (1 + tp_perc)
#             else:
#                 tp_price = price / (1 + tp_perc)

#             try:
#                 total_balance = exchange.fetchTotalBalance()
#             except Exception as e:
#                 print(f"An error occurred while fetching total balance: {e}")
#                 return None

#             order_info = {
#                 "order_id": order_id,
#                 "symbol": symbol,
#                 "timeframe": timeframe,
#                 "buyprice" if order_type == "buy" else "sellprice": price,
#                 "order_qty": order_qty,
#                 "avg_qty": amount,
#                 "side": side,
#                 "tp": tp_price,
#                 "initial_sl": sl_price,
#                 "status": status,
#                 "position_type": position_type,
#                 "in_position": in_position,
#                 "fill_type_status": "taker",
#                 "last_balance": total_balance,
#                 "entry_time": entry_time,
#             }
#             print(f"Order Info: {order_info}")

#             # Load and save order info to order_data_file
#             orders = load_json_file(order_data_file)
#             orders.append(response)
#             save_json_file(order_data_file, orders)

#             # Save response to trade_file
#             trades = load_json_file(trade_file)
#             trades.append(order_info)
#             save_json_file(trade_file, trades)

#             # Update state
#             state["in_position"] = in_position
#             if order_type == "buy":
#                 state["buy_pos"] = True
#             else:
#                 state["sell_pos"] = True

#             # Create or update position info in the pos_file
#             pos_data = {
#                 "symbol": symbol,
#                 "timeframe": timeframe,
#                 "order_id": order_id,
#                 "qty": order_qty,
#                 "tp": tp_price,
#                 "initial_sl": sl_price,
#                 "in_position": in_position,
#                 "position_type": position_type,
#                 "side": side,
#                 "price": price
#             }
#             save_json_file(pos_file, pos_data)  # Save the updated position info directly

#             return order_info, pos_data, state
#         else:
#             print(f"Order placement failed. Status: {response['info']['status']}")
#             return None, None, state

#     except Exception as e:
#         if "insufficientAvailableFunds" in str(e):
#             return handle_insufficient_funds_error(
#                 exchange,
#                 symbol,
#                 timeframe,
#                 amount,
#                 tp_perc,
#                 sl_price,
#                 order_type,
#                 position_type,
#                 state,
#                 order_data_file,
#                 pos_file,
#                 trade_file,
#             )
#         elif "tooManySmallOrders" in str(e):
#             print("Order failed due to tooManySmallOrders error. Adjusting strategy or skipping this order.")
#             return None
#         else:
#             print(f"An error occurred: {e}")
#             return None


def place_stop_loss_order(exchange, symbol, side, amount, sl_price, pos_data):
    print(f"Placing {side} stop-loss order for {amount} units at {sl_price}...")
    stop_loss_price = float(exchange.price_to_precision(symbol, sl_price))
    print(stop_loss_price)
    # Create the stop-loss order
    sl_order_response = exchange.create_order(
        symbol, "stop", side, amount, params={"stopLossPrice": stop_loss_price}
    )
    print("Stop-loss order response:", sl_order_response)

    sl_order_id = sl_order_response["info"].get("order_id")
    order_found = False  # Flag to check if the order is found open

    if sl_order_id:
        open_orders = exchange.fetch_open_orders(symbol=symbol)
        for order in open_orders:
            if order["id"] == sl_order_id:
                sl_order_open = order["info"]["status"] == "untouched"
                if sl_order_open:
                    print("Stop-loss order successfully placed and open.")
                    pos_data["sl_order_id"] = sl_order_id
                    pos_data.setdefault("sl_orders", [])
                    existing_sl_order = next(
                        (o for o in pos_data["sl_orders"] if o["order_id"] == sl_order_id),
                        None,
                    )
                    if existing_sl_order:
                        existing_sl_order["stop_loss_price"].append(stop_loss_price)
                        existing_sl_order["status"] = order["info"]["status"]
                        existing_sl_order["unfilled_size"] = float(
                            order["info"].get("unfilledSize", 0)
                        )
                        existing_sl_order["orderType"] = order["info"].get("orderType")
                        existing_sl_order["last_update"] = order["info"].get("lastUpdateTime")
                    else:
                        pos_data["sl_orders"].append(
                            {
                                "order_id": sl_order_id,
                                "stop_loss_price": [stop_loss_price],
                                "status": order["info"]["status"],
                                "orderType": order["info"].get("orderType"),
                                "unfilled_size": float(order["info"].get("unfilledSize", 0)),
                                "last_update": order["info"].get("lastUpdateTime"),
                            }
                        )
                    order_found = True
        if order_found:
            print(f'Stop-Loss order {sl_order_id} found open with pos_data: {pos_data}')
            return True, pos_data
        else:
            print("Failed to confirm stop-loss order as open.")
    else:
        print("Failed to retrieve stop-loss order ID.")
    return False, pos_data


# def place_take_profit_order(exchange, symbol, side, amount, takeProfit_price, pos_data):
    print(
        f"Placing {side} take-profit order for {amount} units at {takeProfit_price}..."
    )
    tp_price = float(exchange.price_to_precision(symbol, takeProfit_price))
    print(tp_price)
    # Create the take-profit order
    tp_order_response = exchange.create_order(
        symbol,
        "take_profit",
        side,
        amount,
        price=None,
        params={"takeProfitPrice": tp_price},
    )
    print("Take-profit order response:", tp_order_response)

    # Extract the TP order ID and save it if the order was placed successfully
    tp_order_id = tp_order_response["info"].get("order_id")
    if tp_order_id:
        open_orders = exchange.fetch_open_orders(symbol=symbol)
        order_found = False
        for order in open_orders:
            if order["id"] == tp_order_id:
                order_found = True
                tp_order_open = order["info"]["status"] == "untouched"
                if tp_order_open:
                    print("Take-profit order successfully placed and open.")
                    pos_data["tp_order_id"] = tp_order_id
                    # Initialize 'tp_orders' list in pos_data if not present
                    pos_data.setdefault("tp_orders", [])
                    pos_data["tp_orders"].append(
                        {
                            "order_id": tp_order_id,
                            "take_profit_price": [order["info"].get("stopPrice")],
                            "status": order["info"]["status"],
                            "order_type": order["info"].get("orderType"),
                            "unfilled_size": float(
                                order["info"].get("unfilledSize", 0)
                            ),
                            "last_update": order["info"].get("lastUpdateTime"),
                        }
                    )
                    print(f"Take-profit order details updated for {tp_order_id}.")
                break  # Exit loop after finding the matching order

        if order_found:
            print(f'Take-Profit order {tp_order_id} found open with pos_data: {pos_data}')
            return True, pos_data
        else:
            print("Failed to confirm take-profit order as open.")
            return False, pos_data
    else:
        print("Failed to retrieve take-profit order ID.")
    return False, pos_data


# def place_order_to_close_position(
#     exchange,
#     symbol,
#     timeframe,
#     amount,
#     order_type,
#     position_type,
#     fill_type_status,
#     trades_directory='trades',
# ):
#     # Get file paths for the order book, trades, and position info
#     order_data_file, trade_file, pos_file, _, _ = get_file_paths(symbol, trades_directory)
#     try:
#         # Load position info
#         pos_info = load_json_file(pos_file)
#         print(f'Pos info before closing: {pos_info}')

#         # Close position (long or short)
#         if position_type == 'long':
#             response = exchange.create_market_sell_order(symbol=symbol, amount=amount)
#         else:
#             response = exchange.create_market_buy_order(symbol=symbol, amount=amount)

#         print(response)
#         time.sleep(2)

#         # Check if the order is placed successfully
#         if response['info']['status'] == 'placed':
#             order_id = response['info']['order_id']
#             order_events = response['info']['orderEvents']
#             qty = float(order_events[0]['orderPriorExecution']['quantity'])

#             last_order_event = order_events[-1] if order_events else None
#             if last_order_event:
#                 try:
#                     price = float(last_order_event.get('price', 'N/A'))
#                     amount = float(last_order_event.get('amount', 0))
#                     side = last_order_event.get('orderPriorExecution', {}).get('side', 'Unknown')

#                     # Extract exit time from response
#                     exit_time_str = response['info'].get('receivedTime', None)
#                     if exit_time_str:
#                         exit_time = datetime.strptime(exit_time_str, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
#                     else:
#                         exit_time = None

#                 except ValueError as ve:
#                     print("Error converting price to float:", ve)

#                 print(f"{position_type.capitalize()} Position Closed at Market Price")

#                 try:
#                     total_balance = exchange.fetchTotalBalance()
#                 except Exception as e:
#                     print(f"An error occurred while fetching total balance: {e}")
#                     return None

#                 # Create the order_info dictionary
#                 order_info = {
#                     'order_id': order_id,
#                     'symbol': symbol,
#                     'timeframe': timeframe,
#                     'buyprice' if side == 'buy' else 'sellprice': price,
#                     'order_qty': qty,
#                     'avg_qty': 0,
#                     'side': side,
#                     'tp': 0,
#                     'limit': 0,
#                     'status': 'closed',
#                     'position_type': position_type,
#                     'in_position': False,
#                     'fill_type_status': fill_type_status,
#                     'current_balance': total_balance,
#                     'exit_time': exit_time,
#                 }

#                 print(f"Order Info: {order_info}")

#                 # Save order info to files
#                 orders = load_json_file(order_data_file)
#                 orders.append(response)
#                 save_json_file(order_data_file, orders)

#                 trades = load_json_file(trade_file)
#                 trades.append(order_info)
#                 save_json_file(trade_file, trades)

#                 pos_data = {
#                     "symbol": symbol,
#                     "order_id": order_info["order_id"],
#                     "qty": order_info["order_qty"],
#                     "side": order_info["side"],
#                     "price": order_info.get("sellprice" if order_info["position_type"] == "long" else "buyprice", 0.0),
#                     "in_position": False,
#                 }
#                 # Save pos_data after placing position order
#                 save_data(symbol, pos_data)
#                 print(f"Position info after closing: {pos_info}")

#                 # Return the order_info instead of the raw response
#                 return order_info

#             else:
#                 print("No order events found in the response.")
#                 return None
#         else:
#             print(f"Order placement failed. Status: {response['info']['status']}")
#             return None
#     except ccxt.BaseError as e:
#         print("An error occurred:", e)
#         return None


# Define the function to fetch the LTP for any cryptocurrency symbol
def get_kraken_futures_ltp(exchange, symbol):
    ticker = exchange.fetch_ticker(symbol)
    return ticker['last']  # LTP is the last traded price


# def update_pos_data_on_order_edit(symbol, new_sl_price_to_set, pos_data, order_edit_response):
#     """
#     Updates the pos_data dictionary based on the modified order details in the response.
#     """
#     # Extract data from order edit response
#     edit_status = order_edit_response.get("info", {}).get("editStatus", {})
#     order_events = edit_status.get("orderEvents", [])

#     # Check if there are events related to an edit action
#     if not order_events:
#         print("No edit events found in order edit response.")
#         return

#     # Access the latest event data, particularly the 'new' order details post-edit
#     new_order_details = order_events[0].get("new", {})

#     # Extract the required fields from the 'new' data
#     new_sl_trigger_price = float(new_order_details.get("triggerPrice", 0.0))
#     order_type = order_events[0].get(
#         "type", "EDIT"
#     )  # Expected to be 'EDIT' as per response
#     unfilled_size = float(order_edit_response.get("remaining", 0.0))
#     last_update_timestamp = order_edit_response.get(
#         "lastUpdateTimestamp"
#     ) or order_edit_response.get(
#         "datetime"
#     )  # Use 'lastUpdateTimestamp' if available, else 'datetime'
#     # Access the first dictionary in sl_orders and append the new stop-loss price
#     pos_data["sl_orders"][0]["stop_loss_price"].append(new_sl_price_to_set)
#     # Update pos_data with the new stop-loss order information
#     pos_data["sl_orders"].append(
#         {
#             "stop_loss_price": [new_sl_price_to_set],
#             "sl_precision_price": new_sl_trigger_price,
#             "type": order_type,
#             "status": "untouched",  # Status is untouched after an edit
#             "unfilled_size": unfilled_size,
#             "last_update": last_update_timestamp,
#         }
#     )
#     print(f'New stop-loss price for last swing: {new_sl_price_to_set}')
#     print("pos_data updated with new stop-loss order details:")
#     print(pos_data)

#     # Save pos_data to a JSON file
#     save_data(symbol, pos_data)

#     return pos_data


# Define the condition to check whether to modify the stop-loss price
def should_modify_stop_loss(last_row, last_sl_price, ltp, position_type):
    print(f"Evaluating condition for modifying stop loss:")
    print(f"last_row: {last_row}")
    print(f"last_sl_price: {last_sl_price}")
    print(f"ltp: {ltp}")
    print(f"position_type: {position_type}")    

    # Long position condition
    if position_type == "long":
        cond1 = last_row["last_swing_low"] > last_row["prev_swing_low"] # confirms higher low and need modification
        cond2 = last_sl_price is not None
        cond3 = last_sl_price < last_row["last_swing_low"] # confirms new low is higher than the last stop loss set
        cond4 = ltp > last_row["last_swing_low"] # confirms last swing low is higher than the LTP so that it should not be rejected
    # Short position condition
    elif position_type == "short":
        cond1 = last_row["last_swing_high"] < last_row["prev_swing_high"] # confirms lower high and need modification
        cond2 = last_sl_price is not None
        cond3 = last_sl_price > last_row["last_swing_high"] # confirms new high is lower than the last stop loss set
        cond4 = ltp < last_row["last_swing_high"] # confirms last swing high is lower than the LTP so that it should not be rejected 
    else:
        cond1 = cond2 = cond3 = cond4 = False

    print(f"Condition result for stop loss modification: {cond1 and cond2 and cond3 and cond4}")
    return cond1 and cond2 and cond3 and cond4

# Modify the stop-loss order by checking the condition
# def modify_stop_loss(exchange, symbol, pos_data, last_row):
#     print(f"Checking condition to modify stop loss...")
#     # Get the LTP (Last Traded Price)
#     ltp = get_kraken_futures_ltp(exchange, symbol)

#     # Get the last stop loss price from pos_data
#     last_sl_price = pos_data.get("sl_orders", [{}])[-1].get("stop_loss_price", [None])[-1]
#     position_type = pos_data.get("position_type", None)
#     # Check if we need to modify the stop loss
#     if should_modify_stop_loss(last_row, last_sl_price, ltp, position_type):
#         print(f"Condition met to modify stop loss. Modifying stop loss...")

#         # Get the order ID from pos_data
#         sl_order_id = pos_data["sl_orders"][0].get("order_id")
#         sl_order_info = pos_data["sl_orders"][-1]  # Get the last stop-loss order
#         side = "sell" if position_type == "long" else "buy"
#         amount = pos_data.get("qty", 0.0)

#         # Ensure new_sl_trigger_price is assigned as a float
#         if position_type == "long":
#             new_sl_trigger_price = float(last_row["last_swing_low"])
#         elif position_type == "short":
#             new_sl_trigger_price = float(last_row["last_swing_high"])

#         print(f"Placing {side} order for {amount} units at stop-loss price {new_sl_trigger_price}...")
#         new_sl_price = float(exchange.price_to_precision(symbol, new_sl_trigger_price))
#         print(new_sl_price)
#         # Edit the stop-loss order with the new stop price
#         modified_order = exchange.edit_order(
#             sl_order_id,  # The existing stop-loss order ID
#             symbol,  # The trading symbol, e.g., 'BTC/USD'
#             side,  # Side of the order ('buy' or 'sell')
#             "stop",  # The order type ('stop')
#             amount,  # Amount to modify
#             price=None,  # Not needed for stop orders
#             params={"stopPrice": new_sl_price}  # New stop-loss trigger price
#         )

#         print(modified_order)
#         edit_type = modified_order["info"]["editStatus"]["orderEvents"][0]["type"]
#         print(edit_type)
#         response_status = modified_order.get("info", {}).get("result")
#         # Check if the order was successfully modified
#         if (
#             edit_type == "EDIT"
#             and response_status == "success"
#         ):
#             print(
#                 f"Stop-loss order modified successfully. New stop-loss price: {new_sl_price}"
#             )

#             # Call the function to update pos_data
#             updated_pos_data = update_pos_data_on_order_edit(
#                 symbol, new_sl_trigger_price, pos_data, modified_order
#             )

#             return True, updated_pos_data
#         else:
#             print(f"Failed to modify stop-loss order. Status: {modified_order.get('info', {}).get('result')}")
#             return False, pos_data
#     else:
#         print(f"Condition not met to modify stop loss.")
#         return False, pos_data


def calculate_pnl(buyprice, sellprice, positionSize, commission=0.04/100):
    # Calculate taker fee amount
    pnl = (
        sellprice - buyprice) * positionSize
    commission_amount = ((
        sellprice + buyprice) / 2) * positionSize * commission
    # Calculate profit or loss
    pnl = pnl - commission_amount

    return pnl, commission_amount


def fetch_positions_with_retry(exchange, max_retries=3, delay=2):
    """
    Attempts to fetch positions from the exchange with retry logic.
    :param exchange: The exchange object
    :param max_retries: Maximum number of retries
    :param delay: Initial delay between retries (doubles with each retry)
    :return: The fetched positions or None if all retries fail
    """
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} to fetch positions...")
            pos_response = exchange.fetch_positions()
            if pos_response is None:
                raise ValueError("fetch_positions returned None.")
            return pos_response  # Success, return the response
        except Exception as e:
            print(f"Error fetching positions (Attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:  # If not the last attempt
                time.sleep(delay * (2**attempt))  # Exponential backoff
            else:
                print("All retry attempts failed.")
    return None  # Return None after exhausting retries

def displayTrades(direction="Both", initial_balance=10000, **kwargs):
    # st.write('Direction: ', direction)
    # Access the trade data and other results from kwargs
    buydates = kwargs["buydates"]
    buyprices = kwargs["buyprices"]
    selldates = kwargs["selldates"]
    sellprices = kwargs["sellprices"]
    profits = kwargs["profits"]
    entry_type = kwargs["Entry Type"]
    exit_type = kwargs["Exit Type"]
    position_sizes = kwargs["Position Size"]
    profit_or_loss = kwargs["pnl"]
    current_balance = kwargs["current_balance"]

    ct = min(len(buydates), len(selldates))

    # Assuming current_balance is your list of balances
    exit_current_balances = current_balance

    # Create a DataFrame to store the trades
    dfr = pd.DataFrame()
    dfr["buydates"] = buydates[:ct]
    dfr["buyprice"] = buyprices[:ct]
    dfr["selldates"] = selldates[:ct]
    dfr["sellprice"] = sellprices[:ct]
    dfr["profits"] = profits[:ct]
    pnl = pd.Series(profit_or_loss)
    # dfr["commulative_returns"] = (pnl/(pd.Series(current_balance) + pnl) + 1).cumprod()
    dfr["commulative_returns"] = [
        current_balance[i] / initial_balance - 1 for i in range(len(current_balance))
    ][:ct]
    dfr["Entry Type"] = entry_type[:ct]
    dfr["Exit Type"] = exit_type[:ct]
    dfr["Position Size"] = position_sizes[:ct]
    # Add current_balance for each trade
    dfr["Current Balance"] = current_balance[:ct]
    dfr["Profit/Loss"] = profit_or_loss

    # Add a column to indicate the trade side
    dfr["tradeSide"] = np.where(
        dfr["buydates"] < dfr["selldates"], "Long", "Short")
    dfr["Entry Date"] = np.where(
        dfr["tradeSide"] == "Long", dfr["buydates"], dfr["selldates"]
    )
    dfr["Exit Date"] = np.where(
        dfr["tradeSide"] == "Long", dfr["selldates"], dfr["buydates"]
    )
    dfr["Entry Price"] = np.where(
        dfr["tradeSide"] == "Long", dfr["buyprice"], dfr["sellprice"]
    )
    dfr["Exit Price"] = np.where(
        dfr["tradeSide"] == "Long", dfr["sellprice"], dfr["buyprice"]
    )
    # Create a list of column names with the desired display order
    display_order = [
        "Entry Date",
        "Entry Price",
        "Exit Date",
        "Exit Price",
        "profits",
        "commulative_returns",
        "Entry Type",
        "Exit Type",
        "Position Size",
        "Current Balance",
        "Profit/Loss",
        "tradeSide",
    ]

    # Create a copy of the DataFrame with only the columns to be displayed
    dfr_display = dfr[display_order].copy()

    return dfr, dfr_display




def plot_signals(df):
    # Create a candlestick trace
    candlestick = go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color='#e7bf4f',  # Bull candle outline color
        decreasing_line_color='#497ad2',  # Bear candle outline color
        increasing_fillcolor='#e7bf4f',  # Bull candle fill color
        decreasing_fillcolor='#497ad2',  # Bear candle fill color
        name='Candles',
    )

    # Create traces for long and short signals
    long_signals = df[df['long_Signal'] == True]
    short_signals = df[df['short_Signal'] == True]

    trace_long = go.Scatter(x=long_signals.index, y=long_signals['Close'], mode='markers',
                            marker=dict(color='green', size=8), name='Long Signal')
    trace_short = go.Scatter(x=short_signals.index, y=short_signals['Close'], mode='markers',
                             marker=dict(color='red', size=8), name='Short Signal')

    # Create a trace for trailing stop loss (TSL)
    tsl_trace = go.Scatter(x=df.index, y=df['tsl'], mode='lines', name='Trailing Stop Loss',
                           line=dict(color='blue'))

    # # Create a trace to fill area between candles and TSL
    # fill_trace = go.Scatter(x=df.index, y=df[['Close', 'tsl']].max(axis=1), mode='lines',
    #                         fill='tonexty', fillcolor='rgba(255, 0, 0, 0.2)', showlegend=False)

    # Combine all traces
    data = [candlestick, tsl_trace, trace_long, trace_short]  # fill_trace,

    # Split the data into segments based on the trend column
    segments = []
    current_segment = []
    for index, row in df.iterrows():
        if not current_segment or current_segment[-1]['trend'] == row['trend']:
            current_segment.append(row)
        else:
            segments.append(current_segment)
            current_segment = [row]
    segments.append(current_segment)

    trend_up_legend_shown = False
    trend_down_legend_shown = False
    for segment in segments:
        if segment[0]['trend'] == 1:
            if not trend_up_legend_shown:
                trace_up = go.Scatter(x=[row.name for row in segment], y=[row['up'] for row in segment],
                                      mode='lines', name='Trend Up', line=dict(color='green'))
                data.append(trace_up)
                trend_up_legend_shown = True
            else:
                trace_up = go.Scatter(x=[row.name for row in segment], y=[row['up'] for row in segment],
                                      mode='lines', showlegend=False, line=dict(color='green'))
                data.append(trace_up)
        elif segment[0]['trend'] == -1:
            if not trend_down_legend_shown:
                trace_down = go.Scatter(x=[row.name for row in segment], y=[row['dn'] for row in segment],
                                        mode='lines', name='Trend Down', line=dict(color='red'))
                data.append(trace_down)
                trend_down_legend_shown = True
            else:
                trace_down = go.Scatter(x=[row.name for row in segment], y=[row['dn'] for row in segment],
                                        mode='lines', showlegend=False, line=dict(color='red'))
                data.append(trace_down)

    # Layout
    layout = go.Layout(title='SuperTrend Signals with Trailing Stop Loss and Trend Thresholds',
                       xaxis=dict(title='Date'),
                       yaxis=dict(title='Price'))

    # Create figure
    fig = go.Figure(data=data, layout=layout)
    fig.update_layout(xaxis_rangeslider_visible=False)

    return fig


def calculate_position_size(
    method_type: str,
    price_type: str,
    value: float,
    sl_price: float,
    symbol: str,
    exchange,
    backtest=False,
    current_balance: float = None,
    entry_price: float = None,
    leverage=1,
    grid_bot_reserved_balance=100,
):
    debug_prints = []  # Accumulate debug prints here

    if not backtest:
        debug_prints.append(f'Calculating position size for {symbol}...')

    if not backtest:
        # Get the current ticker for the symbol
        ticker = exchange.fetch_ticker(symbol)
    if ticker is None:
        raise ValueError(f"Failed to retrieve ticker for {symbol}")
    entry_price = (
        entry_price if backtest else ticker.get("last", None)
    )  # Use provided entry_price during backtest
    if entry_price is None:
        raise ValueError(f"Failed to retrieve entry price for {symbol}")
    # # Always use USDT as quote currency
    quote_currency = 'USDT'
    # quote_currency = symbol[-3:]
    free_bal = current_balance if backtest else exchange.fetchFreeBalance().get(quote_currency, 0)
    
    # Deduct grid bot reserved balance
    total_bal = free_bal - grid_bot_reserved_balance
    # Ensure total balance is not negative
    if total_bal < 0:
        total_bal = 0
        
    # If total_bal is None, handle it
    if total_bal is None:
        raise ValueError(f"Failed to retrieve USDT balance. Please ensure the account has a valid balance for USDT.")

    if not backtest:
        if total_bal is not None:
            debug_prints.append(f'Current Balance: {total_bal} {quote_currency}')

            # Fetch trading pairs and their details
            markets_data = exchange.load_markets()

            if symbol in markets_data:
                # Get the details of the trading pair
                trading_pair_details = markets_data[symbol]
                debug_prints.append(f'Fetching trading pair details for {symbol}...')
                # Get the minimum order size for BTC (precision value)
                min_asset_order_size = trading_pair_details['precision']['amount']
                debug_prints.append(f'Minimum order size for {symbol} is {min_asset_order_size}')
            else:
                debug_prints.append(f'{symbol} trading pair is not available on the exchange.')

        # if total_bal is None or (total_bal / entry_price) < min_asset_order_size:
        #     # If balance is None or less than minimum order size, switch to USDT
        #     quote_currency = "USDT"
        #     total_bal = exchange.fetchFreeBalance().get(quote_currency, 0)
        #     debug_prints.append(
        #         'Due to insufficient balance in USD, using USDT balance instead.')

            debug_prints.append(
                f'You can buy {total_bal / entry_price} {symbol} at {entry_price} {quote_currency}')

    # Use provided total_bal during backtest
    debug_prints.append("Entry Price: " + str(entry_price))
    debug_prints.append("SL Price: " + str(sl_price))
    debug_prints.append("Total Balance: " + str(total_bal))
    # Initialize qty_ before calculations
    qty_ = 0
    # Calculate position size
    if method_type == "Fixed":
        if price_type == "Quote":
            qty_ = value / entry_price
        elif price_type == "Base":
            qty_ = value
        elif price_type == "Percentage":
            qty_ = (total_bal * (value * 0.01)) / entry_price
    elif method_type == "Dynamic":
        if price_type == "Quote":
            qty_quote = entry_price / ((abs(entry_price - sl_price)) / value)
            qty_ = qty_quote / entry_price
        elif price_type == "Base":
            qty_ = (
                entry_price / ((abs(entry_price - sl_price)) / (value * entry_price))
            ) / entry_price
        elif price_type == "Percentage":
            qty_quote = entry_price / (
                (abs(entry_price - sl_price)) / (total_bal * (value * 0.01))
            )
            qty_ = qty_quote / entry_price

    qty = round(qty_, 3)
    # Enforce the minimum order size
    if 'min_asset_order_size' in locals() and qty < min_asset_order_size:
        qty = min_asset_order_size
        debug_prints.append(f"Quantity was below the minimum order size. Adjusted to {qty}.")
    
    if not backtest:
        debug_prints.append("Quantity Calculated: " + str(qty))
    # Calculate money needed
    money_needed = qty * entry_price
    if not backtest:
        debug_prints.append(f"Money ${money_needed} is needed to buy qty : {qty}")

    # Check if position size exceeds available equity and adjust if needed
    if money_needed > (total_bal * leverage):
        qty_ = total_bal / entry_price
        qty = round(qty_, 3)
        if not backtest:
            debug_prints.append(f"Money needed to buy quantity Exceeded Total Balance, So Adjusting Qty : {qty}")

    if not backtest:
        debug_prints.append("--------------------------------------------------------------------------\n")

    if not backtest:
        # Print all accumulated debug statements
        print('\n'.join(debug_prints))

    return qty


