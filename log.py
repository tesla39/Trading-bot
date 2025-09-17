

bot_logs = []

def log_status(message):

    print(message)  # Optional: keep printing to terminal
    bot_logs.append(message)
    # Limit log size
    if len(bot_logs) > 200:
        bot_logs.pop(0)
