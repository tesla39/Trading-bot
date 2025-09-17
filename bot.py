#from TestBOt.pythondemo import client

from binance_api import create_client
from strategy import selector
from datetime import datetime
from log import log_status
import config

client=create_client()
global S


def run_bot():
    import config
    log_status("Bot started.")
    trading()   
 
def extract_assets(symbol):

    exchange_info = client.get_exchange_info()

    for s in exchange_info['symbols']:
        if s['symbol'] == symbol:
            base_asset = s['baseAsset']
            quote_asset = s['quoteAsset']
            return base_asset, quote_asset
    return None, None


def account_info():
            # log_status("Account info")
            account_info = client.get_account()
            balances = account_info['balances']
            # log_status("Available Asset Balances:")
            
            for asset in balances:
                free = float(asset['free'])
                locked = float(asset['locked'])
                total = free + locked

                if total > 0:
                   log_status(f"{asset['asset']}: Free = {free}, Locked = {locked}, Total = {total}")
                log_status(" ")

            # SYMBOL = input("Enter the trading pair: ")
            SYMBOL='FILUSDC'
            ticker = client.get_symbol_ticker(symbol=SYMBOL)
            price = float(ticker['price'])
            log_status(f"Current price of {SYMBOL}: {price}")
            log_status(" ")

            trades = client.get_my_trades(symbol=SYMBOL)
            # Extract base asset and quote asset


            if not trades:
                log_status("No trade history found.")
            else:
                total_buy = 0.0
                total_sell = 0.0
                buy_qty = 0.0
                sell_qty = 0.0

                log_status("TRADE HISTORY:")
                for trade in trades:
                    qty = float(trade['qty'])
                    price = float(trade['price'])
                    time = datetime.fromtimestamp(trade['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    is_buyer = trade['isBuyer']
                    cost = qty * price

                    if is_buyer:
                        total_buy += cost
                        buy_qty += qty
                        log_status(
                            f"[BUY ] {SYMBOL} | Time: {time} | Qty: {qty:.6f} | Price: ${price:.2f} | Cost: ${cost:.2f}")
                    else:
                        total_sell += cost
                        sell_qty += qty
                        log_status(
                            f"[SELL] {SYMBOL} | Time: {time} | Qty: {qty:.6f} | Price: ${price:.2f} | Revenue: ${cost:.2f}")
                
                 # Calculate average buy and sell price
                avg_buy_price = total_buy / buy_qty if buy_qty else 0
                avg_sell_price = total_sell / sell_qty if sell_qty else 0

                # Calculate matched quantity (only what was bought and sold)
                matched_qty = min(buy_qty, sell_qty)

                # Realized PnL = Profit on matched quantity
                realized_pnl = (avg_sell_price - avg_buy_price) * matched_qty

                # Remaining quantity held
                net_qty = buy_qty - sell_qty

                # Current holdings in wallet
                base_asset, quote_asset = extract_assets(SYMBOL)
                balance_info = client.get_asset_balance(asset=base_asset)
                quantity_held = float(balance_info['free'])

                # # Display
                # log_status("\n--- SUMMARY ---")
                # log_status(f"Total Bought:  {buy_qty:.6f} @ ${total_buy:.2f}")
                # log_status(f"Total Sold:    {sell_qty:.6f} @ ${total_sell:.2f}")
                # log_status(f"Matched Qty:   {matched_qty:.6f}")
                # log_status(f"Avg Buy Price: ${avg_buy_price:.4f}")
                # log_status(f"Avg Sell Price:${avg_sell_price:.4f}")
                # log_status(f"Net Quantity:  {net_qty:.6f} (Bot's PnL tracking only)")
                # log_status(f"Wallet Qty:    {quantity_held:.6f}")
                # log_status(f"Realized PnL:  ${realized_pnl:.2f}")

            open_orders = client.get_open_orders(symbol=SYMBOL)
            # log_status("OPEN TRADES",open_orders)
            # log_status(" ")
        


def trading():
    import config
    from config import bot_running
    exchange_info = client.get_exchange_info()
    symbols = [
        s['symbol'] for s in exchange_info['symbols']
        if s['status'] == 'TRADING' and s['isSpotTradingAllowed']
        
    ]

    valid_pairs = [s['symbol'] for s in exchange_info['symbols'] if s['status'] == 'TRADING']

    # Ask user for input and validate
    while True:
        # S = input("Enter the trading pair you want to buy/sell (e.g., BTCUSDT): ").upper()
        S = 'FARMUSDT'
        if S in valid_pairs:
            log_status(f"Trading pair selected: {S}")
            break
        else:
            log_status(f" '{S}' is not a valid trading pair. Please try again.\n")
    selector(S, "Supertrend", config.bot_running)

    # check strategy
    # log_status("Strategies available:\n", "1.Supertrend\n", "2. RSI\n", "3. HighGain\n")

    # ST = int(input("Enter the strategy number:")) Checking supertrend
    # ST = 1

    # if ST == 1:
    #     selector(S, "Supertrend", bot_running)
    # elif ST == 2:
    #     log_status("RSI isnot available right now")
    #     selector(S, "RSI", bot_running)
    # elif ST == 3:
    #     selector(S, "HighGain", bot_running)

    # PASS(S)




