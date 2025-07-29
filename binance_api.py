from binance.client import Client
import pandas as pd
import time
import ta
import os
from dotenv import load_dotenv

# 1. Parameters
SYMBOL = 'BTCUSDT'
QUANTITY = 0.001
ATR_PERIOD = 10
MULTIPLIER = 3

load_dotenv()

# 2. API Setup (Testnet)
def create_client():
    #SYMBOL = 'BTCUSDT'
    API_KEY=os.getenv("API_KEY")
    API_SECRET=os.getenv("API_SECRET")
    client= Client(API_KEY, API_SECRET, testnet=True)
    return client


# 3. Fetch OHLCV Data
def fetch_candles(SYMBOL, interval, lookback=200):
    client = create_client()

    # Fetch enough candles for any indicator — default 100 or user-defined
    klines = client.get_klines(symbol=SYMBOL, interval=interval, limit=lookback)

    df = pd.DataFrame(klines, columns=[
        'time', 'open', 'high', 'low', 'close', 'volume',
        'closetime', 'qav', 'numtrades', 'tbv', 'tqv', 'ignore'
    ])

    # Convert to proper types
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)

    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df.set_index('time', inplace=True)

    # Return only relevant columns for indicators
    return df



