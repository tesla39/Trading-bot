from binance.client import Client
import pandas as pd
import time
import ta

# 1. API Setup (Testnet)
API_KEY = '0da6LHcJOuj5wnGRTu6Nyzarm4dEh1WdL4a0BRAdsxnYU00faApM6wEdYpkM6sFP'
API_SECRET = '1aFiClFOmuCgsXoBvvaUiHxCAFcbP1sSS0ZUMcbyhJDRkroFJfNsmFXtnt4vhBxt'
client = Client(API_KEY, API_SECRET, testnet=True)

# 2. Parameters
SYMBOL = 'BTCUSDT'
QUANTITY = 0.001
ATR_PERIOD = 10
MULTIPLIER = 3

# 3. Fetch OHLCV Data
def fetch_candles():
    klines = client.get_klines(symbol=SYMBOL, interval='1m', limit=ATR_PERIOD+20)
    df = pd.DataFrame(klines)
    df.columns = ['time','open','high','low','close','volume','closetime','qav','numtrades','tbv','tqv','ignore']
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    return df

df = fetch_candles()