#from TestBOt.pythondemo import client
from binance_api import create_client
from strategy import selector
from datetime import datetime

client=create_client()
global S
# S='BTCUSDT'

def extract_assets(symbol):

    exchange_info = client.get_exchange_info()

    for s in exchange_info['symbols']:
        if s['symbol'] == symbol:
            base_asset = s['baseAsset']
            quote_asset = s['quoteAsset']
            return base_asset, quote_asset
    return None, None

    # known_quote_assets = ['USDT', 'BUSD', 'BTC', 'ETH']

    # for quote in known_quote_assets:
    #     if symbol.endswith(quote):
    #         base_asset = symbol.replace(quote, '')
    #         quote_asset = quote
    #         return base_asset, quote_asset
    # return None, None

def action(choice):
    match choice:
        
        case 1:
            print("Account info")
            account_info = client.get_account()
            balances = account_info['balances']
            print("Available Asset Balances:")
            
            for asset in balances:
                free = float(asset['free'])
                locked = float(asset['locked'])
                total = free + locked

                if total > 0:
                   print(f"{asset['asset']}: Free = {free}, Locked = {locked}, Total = {total}")
                print(" ")

            # SYMBOL = input("Enter the trading pair: ")
            SYMBOL='FILUSDC'
            ticker = client.get_symbol_ticker(symbol=SYMBOL)
            price = float(ticker['price'])
            print(f"Current price of {SYMBOL}: {price}")
            print(" ")

            trades = client.get_my_trades(symbol=SYMBOL)
            # Extract base asset and quote asset


            if not trades:
                print("No trade history found.")
            else:
                total_buy = 0.0
                total_sell = 0.0
                buy_qty = 0.0
                sell_qty = 0.0

                print("TRADE HISTORY:")
                for trade in trades:
                    qty = float(trade['qty'])
                    price = float(trade['price'])
                    time = datetime.fromtimestamp(trade['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    is_buyer = trade['isBuyer']
                    cost = qty * price

                    if is_buyer:
                        total_buy += cost
                        buy_qty += qty
                        print(
                            f"[BUY ] {SYMBOL} | Time: {time} | Qty: {qty:.6f} | Price: ${price:.2f} | Cost: ${cost:.2f}")
                    else:
                        total_sell += cost
                        sell_qty += qty
                        print(
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

                # Display
                print("\n--- SUMMARY ---")
                print(f"Total Bought:  {buy_qty:.6f} @ ${total_buy:.2f}")
                print(f"Total Sold:    {sell_qty:.6f} @ ${total_sell:.2f}")
                print(f"Matched Qty:   {matched_qty:.6f}")
                print(f"Avg Buy Price: ${avg_buy_price:.4f}")
                print(f"Avg Sell Price:${avg_sell_price:.4f}")
                print(f"Net Quantity:  {net_qty:.6f} (Bot's PnL tracking only)")
                print(f"Wallet Qty:    {quantity_held:.6f}")
                print(f"Realized PnL:  ${realized_pnl:.2f}")

            open_orders = client.get_open_orders(symbol=SYMBOL)
            print("OPEN TRADES",open_orders)
            print(" ")
        
        case 2:

            account_info = client.get_account()

            print("Exchange Assets[ex: ETH to USDT]")
            
            assets=input("Enter the asset to convert: ")
            ticker = client.get_symbol_ticker(symbol=assets)
            price = float(ticker['price'])
            print(f"Current price of {assets}: {price}")
            
            X='SELL'
             # Step 2: Determine base and quote
            base_asset = input("Enter the asset you want to convert (e.g., ETH): ").upper()
            qty = input(f"Enter the quantity of {base_asset} you want to convert: ")
            qty = float(qty)
            
            to_asset = input("Enter the asset to convert into (e.g., USDT): ").upper()

            if base_asset + to_asset == assets:
             X = 'SELL'
            elif to_asset + base_asset == assets:
             X = 'BUY'
            else:
                print(" Symbol and assets don't match correctly. Please check your input.")
            

              # Step 4: Place order
            if X == 'SELL':
              print(f"Placing SELL order for {qty} {base_asset}...")
              order = client.order_market_sell(symbol=assets, quantity=qty)
            else:
              print(f"Placing BUY order for {qty} {base_asset}...")
              order = client.order_market_buy(symbol=assets, quantity=qty)

            print("Order placed successfully!")
            print("Order Details:")
            for key, value in order.items():
             print(f"{key}: {value}")
   



        case 3:
            print("Trading pair examples:")

            exchange_info = client.get_exchange_info()
            symbols = [
                s['symbol'] for s in exchange_info['symbols']
                if s['status'] == 'TRADING' and s['isSpotTradingAllowed']
            ]
            # Get top 50 symbols (sorted alphabetically for consistency)
            top_500 = sorted(symbols)[:500]
            # Print the top 50 tradable symbols
            print("Top 50 tradable pairs on Testnet:")
            for i, symbol in enumerate(top_500, start=1):
                print(f"{i}. {symbol}")

            valid_pairs = [s['symbol'] for s in exchange_info['symbols'] if s['status'] == 'TRADING']

            # Ask user for input and validate
            while True:
                # S = input("Enter the trading pair you want to buy/sell (e.g., BTCUSDT): ").upper()
                S='FILUSDC'
                if S in valid_pairs:
                    print(f"'{S}' is a valid trading pair. Proceeding...")
                    break
                else:
                    print(f" '{S}' is not a valid trading pair. Please try again.\n")

            #check strategy
            print("Strategies available:\n", "1.Supertrend\n", "2. RSI\n", "3. HighGain\n")
            
            
            #ST= int(input("Enter the strategy number:")) Checking supertrend
            ST=1

            if ST==1:
                selector(S,"Supertrend")
            elif ST==2:
                print("RSI isnot available right now")
                selector(S,"RSI")
            elif ST==3:
                selector(S,"HighGain")

                # PASS(S)

        case 4:
            print("On Progress...")
        case _:
            print("On Progress...")



print("___________Select the option_________")
print("1. Account info ")
print("2. Exchange assets")
print("3. Buy / Sell")
print("4. Buy / Hold")
print("5. Sell / Hold")
print("6. Exit")

#val=int(input())
val=3
action(val)
