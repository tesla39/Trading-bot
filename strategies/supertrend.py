#CALCULATING SUPERTREND
import ta

import pandas as pd
import numpy as np

atr_period=10
multiplier=3.0


def calculate_supertrend(df, period=10, multiplier=3):
    # ATR calculation
    hl = df['high'] - df['low']
    hc = (df['high'] - df['close'].shift()).abs()
    lc = (df['low'] - df['close'].shift()).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()

    # Basic bands
    upperband = (df['high'] + df['low']) / 2 + multiplier * atr
    lowerband = (df['high'] + df['low']) / 2 - multiplier * atr

    # Final bands
    final_upperband = upperband.copy()
    final_lowerband = lowerband.copy()

    for i in range(1, len(df)):
        if df['close'].iloc[i-1] <= final_upperband.iloc[i-1]:
            final_upperband.iloc[i] = min(upperband.iloc[i], final_upperband.iloc[i-1])
        else:
            final_upperband.iloc[i] = upperband.iloc[i]

        if df['close'].iloc[i-1] >= final_lowerband.iloc[i-1]:
            final_lowerband.iloc[i] = max(lowerband.iloc[i], final_lowerband.iloc[i-1])
        else:
            final_lowerband.iloc[i] = lowerband.iloc[i]

    # Supertrend calculation
    supertrend = pd.Series(index=df.index, dtype=float)
    trend = pd.Series(index=df.index, dtype=float)

    for i in range(period, len(df)):
        if df['close'].iloc[i] > final_upperband.iloc[i-1]:
            supertrend.iloc[i] = final_lowerband.iloc[i]
            trend.iloc[i] = 1   # bullish
        elif df['close'].iloc[i] < final_lowerband.iloc[i-1]:
            supertrend.iloc[i] = final_upperband.iloc[i]
            trend.iloc[i] = -1  # bearish
        else:
            supertrend.iloc[i] = supertrend.iloc[i-1]
            trend.iloc[i] = trend.iloc[i-1]

    df['Supertrend'] = supertrend
    df['Trend'] = trend
    return df

def get_signal(df):
    sell_count=0
    buy_count=0

    if len(df) < 2:
        return "HOLD"

    if df['Trend'].iloc[-1] == 1 and df['Trend'].iloc[-2] == -1:
        sell_count+=1
        buy_count=0

        if sell_count>=2: return "HOLD"
        return "BUY"
    
    elif df['Trend'].iloc[-1] == -1 and df['Trend'].iloc[-2] == 1:
        buy_count+=1
        sell_count=0

        if buy_count>=2: return "HOLD"
        return "SELL"
    else:
        return "HOLD"

# import pandas as pd
# import numpy as np

# # ------------------ 1. Calculating Supertrend ------------------
# def calculate_supertrend(df, atr_period=10, multiplier=3.0):
#     """
#     Supertrend with 'confirmed after close' buy/sell logic.
#     df: pandas DataFrame with columns: ['Open', 'high', 'low', 'close']
#     """
#     # --- ATR calculation ---
#     hl = df['high'] - df['low']
#     hc = np.abs(df['high'] - df['close'].shift())
#     lc = np.abs(df['low'] - df['close'].shift())
#     tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
#     atr = tr.rolling(atr_period).mean()

#     # --- Basic bands ---
#     hl2 = (df['high'] + df['low']) / 2
#     upperband = hl2 + (multiplier * atr)
#     lowerband = hl2 - (multiplier * atr)

#     # --- Final bands ---
#     final_upperband = upperband.copy()
#     final_lowerband = lowerband.copy()

#     for i in range(1, len(df)):
#         if (upperband[i] < final_upperband[i-1]) or (df['close'][i-1] > final_upperband[i-1]):
#             final_upperband[i] = upperband[i]
#         else:
#             final_upperband[i] = final_upperband[i-1]

#         if (lowerband[i] > final_lowerband[i-1]) or (df['close'][i-1] < final_lowerband[i-1]):
#             final_lowerband[i] = lowerband[i]
#         else:
#             final_lowerband[i] = final_lowerband[i-1]

#     # --- Trend direction ---
#     direction = np.ones(len(df))
#     for i in range(1, len(df)):
#         if df['close'][i] > final_upperband[i-1]:
#             direction[i] = -1  # uptrend
#         elif df['close'][i] < final_lowerband[i-1]:
#             direction[i] = 1   # downtrend
#         else:
#             direction[i] = direction[i-1]

#     # --- Confirmed buy/sell signals ---
#     buy_signal = (pd.Series(direction).shift(2) > 0) & (pd.Series(direction).shift(1) < 0)
#     sell_signal = (pd.Series(direction).shift(2) < 0) & (pd.Series(direction).shift(1) > 0)

#     # --- Append results to DataFrame ---
#     df['Supertrend'] = np.where(direction < 0, final_lowerband, final_upperband)
#     df['Direction'] = direction
#     df['Buy'] = buy_signal
#     df['Sell'] = sell_signal

#     return df

# # ------------------ 2. Strategy Logic ------------------
# def check_signal(df):
#     """
#     Returns: 'BUY', 'SELL', or 'HOLD' based on the latest confirmed signal.
#     """
#     if df['Buy'].iloc[-1]:
#         return 'BUY'
#     elif df['Sell'].iloc[-1]:
#         return 'SELL'
#     else:
#         return 'HOLD'


