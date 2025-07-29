from ta.volatility import AverageTrueRange
from ta.momentum import RSIIndicator
from ta.trend import MACD

def calculate_high_gain(df):
    # Step 1: Supertrend
    MULTIPLIER = 3
    ATR_PERIOD = 10

    atr = AverageTrueRange(df['high'], df['low'], df['close'], window=ATR_PERIOD).average_true_range()
    hl2 = (df['high'] + df['low']) / 2
    upperband = hl2 + (MULTIPLIER * atr)
    lowerband = hl2 - (MULTIPLIER * atr)

    in_uptrend = [True]
    supertrend = [0.0]

    for i in range(1, len(df)):
        if df['close'].iloc[i] > upperband.iloc[i - 1]:
            in_uptrend.append(True)
        elif df['close'].iloc[i] < lowerband.iloc[i - 1]:
            in_uptrend.append(False)
        else:
            in_uptrend.append(in_uptrend[-1])

        if in_uptrend[-1]:
            lowerband.iloc[i] = max(lowerband.iloc[i], lowerband.iloc[i - 1])
            supertrend.append(lowerband.iloc[i])
        else:
            upperband.iloc[i] = min(upperband.iloc[i], upperband.iloc[i - 1])
            supertrend.append(upperband.iloc[i])

    df['supertrend'] = supertrend

    # Step 2: RSI
    df['rsi'] = RSIIndicator(df['close'], window=14).rsi()

    # Step 3: MACD Histogram
    macd = MACD(df['close'], window_slow=26, window_fast=12, window_sign=9)
    df['macd_hist'] = macd.macd_diff()

    # Step 4: Volume Spike
    df['vol_ma'] = df['volume'].rolling(window=10).mean()
    df['vol_spike'] = df['volume'] > df['vol_ma']

    return df


def check_signal(df):
    if len(df) < 2:
        return 'HOLD'

    last = df.iloc[-1]
    prev = df.iloc[-2]

    if (
        last['close'] > last['supertrend'] and
        last['rsi'] < 45 and
        last['macd_hist'] > 0 and prev['macd_hist'] < 0 and
        last['vol_spike']
    ):
        return 'BUY'

    elif (
        last['close'] < last['supertrend'] or
        last['rsi'] > 65 or
        last['macd_hist'] < 0
    ):
        return 'SELL'

    else:
        return 'HOLD'