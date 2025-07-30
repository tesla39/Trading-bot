from binance_api import create_client
from binance_api import fetch_candles
import time
import ta
import pandas as pd
from datetime import datetime
from email_notification import send_email
from pnl import calculate_pnl
from strategies.supertrend import *
from strategies.high_gain import *

client = create_client()
ATR_PERIOD = 10
MULTIPLIER = 3

#Helper functions
def get_price(symbol):
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker['price'])


#Helper functions
def extract_assets(symbol):

    exchange_info = client.get_exchange_info()

    for s in exchange_info['symbols']:
        if s['symbol'] == symbol:
            base_asset = s['baseAsset']
            quote_asset = s['quoteAsset']
            return base_asset, quote_asset
    return None, None

#Helper function
def get_min_notional(symbol):
    info = client.get_symbol_info(symbol)
    if not info:
        raise ValueError(f"Invalid symbol: {symbol}")

    for f in info['filters']:
        if f['filterType'] == 'NOTIONAL' or f['filterType'] == 'notional':
            # some symbols use 'notional', some use 'minNotional'
            return float(f.get('minNotional', f.get('notional', 10.0)))

    raise ValueError(f" MIN_NOTIONAL filter not found for {symbol}")

def get_valid_quantity(symbol):
    price = get_price(symbol)
    min_notional = get_min_notional(symbol)

    # Add small buffer to avoid Binance rounding failure (e.g., +0.5%)
    buffer = 1.005
    raw_qty = (min_notional * buffer) / price

    return float(format_quantity(symbol, raw_qty))


#6. Place Orders
def manual_mode(symbol, interval='5m'):
    df = fetch_candles(symbol, interval, lookback=200)
    df = calculate_supertrend(df)
    signal = check_signal(df)
    print(f"Manual Check: Signal is {signal}")
    quantity = float(input("Enter quantity to trade: "))
    place_order(signal, symbol, quantity)


#placing order
def place_order(signal, symbol, quantity):
    base_asset, quote_asset = extract_assets(symbol)

    # Fetch account balances
    account_info = client.get_account()
    balances = {asset['asset']: float(asset['free']) for asset in account_info['balances']}

    if signal == 'BUY':
        # Get the latest price to calculate required quote asset

        price = get_price(symbol)
        required_quote = price * quantity

        if balances.get(quote_asset, 0) >= required_quote:
            print(f"Placing BUY Order for {quantity} {base_asset} (~{required_quote:.2f} {quote_asset})")
            client.order_market_buy(symbol=symbol, quantity=quantity)
        else:
            print(
                f"Not enough {quote_asset}. Required: {required_quote:.2f}, Available: {balances.get(quote_asset, 0):.2f}")

    elif signal == 'SELL':
        if balances.get(base_asset, 0) >= quantity:
            print(f"Placing SELL Order for {quantity} {base_asset}")
            client.order_market_sell(symbol=symbol, quantity=quantity)
        else:
            print(
                f"Not enough {base_asset} to sell. Required: {quantity}, Available: {balances.get(base_asset, 0):.6f}")
    else:
        print("No valid signal, holding position.")

#FOR MANUAL INPUT
# def format_quantity(symbol, quantity):
#     # Default to 6 decimal places; customize per symbol if needed
#     return "{:.6f}".format(quantity).rstrip('0').rstrip('.')  # Clean trailing zeros and dot


def get_step_size(symbol):
    info = client.get_symbol_info(symbol)
    for f in info['filters']:
        if f['filterType'] == 'LOT_SIZE':
            return float(f['stepSize'])

def format_quantity(symbol, quantity):
    step = get_step_size(symbol)
    return format(quantity - (quantity % step), f'.{str(step)[::-1].find(".")}f')

        
def get_minimum_quantity(symbol):
    price = get_price(symbol)
    min_notional = get_min_notional(symbol)
    raw_qty = min_notional / price
    return float(format_quantity(symbol, raw_qty))

def selector(SYM, strategy):
    symbol=SYM
    STRATEGY=strategy
    mode = "auto"
    signal = ""
    #In FILUSDC, FIL is the base asset and USDC is the quote asset — to trade, you buy FIL using USDC.
    price = get_price(symbol)

    # symbol = input("Enter symbol (e.g., BTCUSDT): ").upper()
    # mode = input("Enter mode (manual/auto): ").strip().lower()
    # quote_asset = client.get_symbol_info(symbol)['quoteAsset']
    # min_notional = get_min_notional(symbol)
    # signal=""

    # while True:
    #     quantity= float(input(f"Enter base quantity for {symbol}: "))
    #     quantity = float(format_quantity(symbol, quantity))
    #     price=get_price(symbol)
    #     notional = quantity * price

    #     if notional < min_notional:
    #         print(f" Notional value = {notional:.8f} {quote_asset} is below minimum {min_notional:.8f} {quote_asset}")
    #     else:
    #         break

    if mode == "manual":
        manual_mode(symbol)

    elif mode == "auto":
            print("Enter the duration to run your bot:")
            # hours = int(input("Hours: "))
            # minutes = int(input("Minutes: "))
            # seconds = int(input("Seconds: "))
            hours = int(2)
            minutes = int(2)
            seconds = int(1)

            total_seconds = hours * 3600 + minutes * 60 + seconds
            end_time = time.time() + total_seconds

            print(f"Running bot for {hours}h {minutes}m {seconds}s...")
            order_log = []

            try:
                
                while time.time() < end_time:
                    df = fetch_candles(symbol, '5m', lookback=200)

                    if STRATEGY=="Supertrend" :
                        df = calculate_supertrend(df)
                        signal = check_signal(df)
                    
                    elif STRATEGY=="HighGain" :
                        df = calculate_high_gain(df)
                        signal = check_signal(df)
                      
                    #print(f"[{datetime.now()}] Latest signal: {signal}")

                    if signal in ['BUY', 'SELL']:
                        quantity=get_valid_quantity(symbol)
                        price = get_price(symbol)
                        order_log.append({"type": signal, "price": price, "qty": quantity, "time": datetime.now()})
                        place_order(signal, symbol, quantity)

                    time.sleep(60)
            except KeyboardInterrupt:
                print("\n Bot manually stopped by user.")

            pnl_summary = calculate_pnl(order_log,symbol)
            send_email("🔔 Binance Bot Report", pnl_summary, "mbkk36900@gmail.com")
            print("Auto mode finished.")
    else:
        print("Invalid mode selected. Choose 'manual' or 'auto'.")



