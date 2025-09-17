def calculate_fibonacci_retracement(df):
    recent_high = df['high'].max()
    recent_low = df['low'].min()

    levels = {
        '0.0': recent_high,
        '0.236': recent_high - 0.236 * (recent_high - recent_low),
        '0.382': recent_high - 0.382 * (recent_high - recent_low),
        '0.5': recent_high - 0.5 * (recent_high - recent_low),
        '0.618': recent_high - 0.618 * (recent_high - recent_low),
        '0.786': recent_high - 0.786 * (recent_high - recent_low),
        '1.0': recent_low,
    }

    for key, value in levels.items():
        df[f'fib_{key}'] = value

    return df

def check_signal(df):
    last_close = df['close'].iloc[-1]
    fib_618 = df['fib_0.618'].iloc[-1]
    fib_382 = df['fib_0.382'].iloc[-1]

    if last_close > fib_382:
        return 'BUY'
    elif last_close < fib_618:
        return 'SELL'
    else:
        return 'HOLD'
