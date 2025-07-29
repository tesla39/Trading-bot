def calculate_pnl(orders,symbol):
    total_buy_qty = total_sell_qty = 0
    total_buy_cost = total_sell_value = 0

    for order in orders:
        if order["type"] == "BUY":
            total_buy_qty += order["qty"]
            total_buy_cost += order["qty"] * order["price"]
        elif order["type"] == "SELL":
            total_sell_qty += order["qty"]
            total_sell_value += order["qty"] * order["price"]

    net_qty = total_buy_qty - total_sell_qty
    pnl = total_sell_value - total_buy_cost

    summary = f"""\

    Dear User,

    Here is the summary of your recent bot trading session:

    Bot Session Summary 
    ---------------------------------------
    Symbol         : {symbol}
    Total BUY      : {total_buy_qty} units at avg price {total_buy_cost / total_buy_qty if total_buy_qty else 0:.2f}
    Total SELL     : {total_sell_qty} units at avg price {total_sell_value / total_sell_qty if total_sell_qty else 0:.2f}
    Net Quantity   : {net_qty}
    PnL            : {'Profit' if pnl >= 0 else 'Loss'} of {pnl:.2f} USDT
    ---------------------------------------

    If you have any questions or need assistance with your trades, feel free to reach out.

    Best regards,  
    MaxGain Bot
    """

    return summary
