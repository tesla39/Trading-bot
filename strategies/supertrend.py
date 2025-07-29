#CALCULATING SUPERTREND
import ta

def calculate_supertrend(df):
    MULTIPLIER = 3
    ATR_PERIOD = 10
    
    atr = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], ATR_PERIOD).average_true_range()
    hl2 = (df['high'] + df['low']) / 2
    upperband = hl2 + (MULTIPLIER * atr)
    lowerband = hl2 - (MULTIPLIER * atr)

    # Ensure bands have same index as df
    upperband = upperband.reset_index(drop=True)
    lowerband = lowerband.reset_index(drop=True)
    df = df.reset_index(drop=True)
    df['supertrend'] = 0.0

    in_uptrend = True

    for i in range(1, len(df)):
        if df['close'].iloc[i] > upperband.iloc[i - 1]:
            in_uptrend = True
        elif df['close'].iloc[i] < lowerband.iloc[i - 1]:
            in_uptrend = False

        # Sticky band logic
        if in_uptrend:
            lowerband.iloc[i] = max(lowerband.iloc[i], lowerband.iloc[i - 1])
            df.loc[i, 'supertrend'] = lowerband.iloc[i]
        else:
            upperband.iloc[i] = min(upperband.iloc[i], upperband.iloc[i - 1])
            df.loc[i, 'supertrend'] = upperband.iloc[i]

    return df

# 5. Strategy Logic
def check_signal(df):
    if df['close'].iloc[-1] > df['supertrend'].iloc[-1]:
        return 'BUY'
    elif df['close'].iloc[-1] < df['supertrend'].iloc[-1]:
        return 'SELL'
    else:
        return 'HOLD'