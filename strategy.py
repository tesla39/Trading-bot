from binance_api import create_client 
from binance_api import fetch_candles
import time
import ta
import config
import pandas as pd
from datetime import datetime
from email_notification import send_email
from pnl import calculate_pnl
from strategies.supertrend import *
from strategies.high_gain import *
import math
from decimal import Decimal, ROUND_UP, getcontext
from binance.exceptions import BinanceAPIException
from log import log_status


client = create_client()
ATR_PERIOD = 10
MULTIPLIER = 3

# # --- Logging Helper ---
# try:
#     from bot import log_status
# except ImportError:
#     def log_status(msg):
#         print(msg)


# ---------------------- Helper Functions ----------------------
def get_price(symbol):
    """Fetch the latest market price for a symbol."""
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker['price'])


def extract_assets(symbol):
    """Return base and quote assets from symbol info."""
    exchange_info = client.get_exchange_info()
    for s in exchange_info['symbols']:
        if s['symbol'] == symbol:
            return s['baseAsset'], s['quoteAsset']
    return None, None

def get_symbol_filters(symbol):
    """Get all filters for a given symbol."""
    info = client.get_symbol_info(symbol)
    if not info:
        raise ValueError(f"Invalid symbol: {symbol}")
    return info['filters']

def get_min_notional(symbol):
    """Return minNotional or notional filter value."""
    for f in get_symbol_filters(symbol):
        if f['filterType'].upper() in ['NOTIONAL', 'MIN_NOTIONAL']:
            return float(f.get('minNotional', f.get('notional', 10.0)))
    raise ValueError(f"MIN_NOTIONAL filter not found for {symbol}")

def get_lot_size(symbol):
    """Return LOT_SIZE details: minQty, maxQty, stepSize."""
    for f in get_symbol_filters(symbol):
        if f['filterType'] == 'LOT_SIZE':
            return {
                "minQty": float(f['minQty']),
                "maxQty": float(f['maxQty']),
                "stepSize": float(f['stepSize'])
            }
    raise ValueError(f"LOT_SIZE filter not found for {symbol}")

def format_quantity(symbol, quantity):
    """Adjust quantity to meet Binance LOT_SIZE rules."""
    lot = get_lot_size(symbol)
    step = lot['stepSize']
    min_qty = lot['minQty']
    max_qty = lot['maxQty']

    if quantity < min_qty:
        quantity = min_qty
    elif quantity > max_qty:
        quantity = max_qty

    # Adjust to step size
    precision = int(round(-math.log(step, 10), 0))
    quantity = math.floor(quantity / step) * step
    return float(f"{quantity:.{precision}f}")

def get_valid_quantity(symbol):
    """Calculate quantity that meets BOTH minNotional and LOT_SIZE."""
    price = get_price(symbol)
    min_notional = get_min_notional(symbol)

    # Add a small buffer to avoid rounding issues
    buffer = 1.005
    raw_qty = (min_notional * buffer) / price

    return format_quantity(symbol, raw_qty)



#Helper function
# def get_min_notional(symbol):
#     info = client.get_symbol_info(symbol)
#     if not info:
#         raise ValueError(f"Invalid symbol: {symbol}")

#     for f in info['filters']:
#         if f['filterType'] == 'NOTIONAL' or f['filterType'] == 'notional':
#             # some symbols use 'notional', some use 'minNotional'
#             return float(f.get('minNotional', f.get('notional', 10.0)))

#     raise ValueError(f" MIN_NOTIONAL filter not found for {symbol}")

# def get_valid_quantity(symbol):
    
#     min_notional = get_min_notional(symbol)
#     #quote_asset = client.get_symbol_info(symbol)['quoteAsset']
#     price = get_price(symbol)
#     # Add small buffer to avoid Binance rounding failure (e.g., +0.5%)
#     buffer = 1.005
#     raw_qty = (min_notional * buffer) / price

#     return float(format_quantity(symbol, raw_qty))


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
            log_status(f"Placing BUY Order for {quantity} {base_asset} (~{required_quote:.2f} {quote_asset})")
            print(f"Placing BUY Order for {quantity} {base_asset} (~{required_quote:.2f} {quote_asset})")
            client.order_market_buy(symbol=symbol, quantity=quantity)
        else:
            log_status(f"Not enough {quote_asset}. Required: {required_quote:.2f}, Available: {balances.get(quote_asset, 0):.2f}")
            print(
                f"Not enough {quote_asset}. Required: {required_quote:.2f}, Available: {balances.get(quote_asset, 0):.2f}")

    elif signal == 'SELL':
        if balances.get(base_asset, 0) >= quantity:
            log_status(f"Placing SELL Order for {quantity} {base_asset}")
            print(f"Placing SELL Order for {quantity} {base_asset}")
            client.order_market_sell(symbol=symbol, quantity=quantity)
        else:
            log_status(f"Not enough {base_asset} to sell. Required: {quantity}, Available: {balances.get(base_asset, 0):.6f}")
            print(
                f"Not enough {base_asset} to sell. Required: {quantity}, Available: {balances.get(base_asset, 0):.6f}")
    else:
        print("No valid signal, holding position.")





# def manual_mode(symbol, interval='5m'):
#     """Manual mode: checks signal and lets user place order."""
#     df = fetch_candles(symbol, interval, lookback=200)
#     df = calculate_supertrend(df)
#     signal = check_signal(df)
#     log_status(f"Manual Check: Signal is {signal}")
#     quantity = float(input("Enter quantity to trade: "))
#     place_order(signal, symbol, quantity)


def selector(SYM, strategy, status):
    import config 
    
    symbol = SYM
    STRATEGY = strategy
    mode = "auto"
    signal = ""    
    price = get_price(symbol)
    # min_notional = get_min_notional(symbol)
    notional=get_min_notional(symbol)
    quantity=get_valid_quantity(symbol)

    print(f"Ready to trade {symbol} worth {notional:.8f}")

    if mode == "manual":
        manual_mode(symbol)

    elif mode == "auto":
        while config.bot_running:
            
            log_status("Enter the duration to run your bot:")
            hours, minutes, seconds = 2, 2, 1
            total_seconds = hours * 3600 + minutes * 60 + seconds
            end_time = time.time() + total_seconds

            log_status(f"Running bot for {hours}h {minutes}m {seconds}s...")
            order_log = []

            try:
                while time.time() < end_time and config.bot_running:
                    df = fetch_candles(symbol, '5m', lookback=200)

                    if STRATEGY == "Supertrend":
                        df = calculate_supertrend(df)
                        signal = check_signal(df)
                    elif STRATEGY == "HighGain":
                        df = calculate_high_gain(df)
                        signal = check_signal(df)

                    if signal in ['BUY', 'SELL']:
                        quantity = get_valid_quantity(symbol)
                        price = get_price(symbol)
                        order_log.append({"type": signal, "price": price, "qty": quantity, "time": datetime.now()})
                        place_order(signal, symbol, quantity)

                    time.sleep(60)

            except KeyboardInterrupt:
                log_status("\n Bot manually stopped by user.")

            pnl_summary = calculate_pnl(order_log, symbol)
            send_email("🔔 Binance Bot Report", pnl_summary, "mbkk36900@gmail.com")
            log_status("Auto mode finished.")
    else:
        log_status("Invalid mode selected. Choose 'manual' or 'auto'.")
