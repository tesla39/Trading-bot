from flask import Flask, render_template, request, jsonify
from threading import Thread
from bot import run_bot
from log import bot_logs
from config import bot_running
import config  # Import from central state
app = Flask(__name__)

bot_thread = None
bot_running = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manual-mode')
def manual_start():
    return render_template('Manual.html')

@app.route('/start-manual', methods=['POST'])
# def start_manual():
#     # Get form data
#     bot_duration = request.form.get('bot_duration')
#     trading_mode = request.form.get('trading_mode')
#     trading_pair = request.form.get('trading_pair')
#     total_amount = request.form.get('total_amount')
    
#     # Here you would implement your manual bot starting logic
#     # using the parameters from the form
    
#     log_status(f"Manual bot started with duration: {bot_duration}, mode: {trading_mode}, pair: {trading_pair}, amount: {total_amount}")
    
#     return jsonify({"status": "manual started"})

@app.route('/start-bot', methods=['POST'])
def start_bot():
    global bot_thread
    #from config import bot_running 
    if not config.bot_running:
        bot_thread = Thread(target=run_bot, daemon=True)
        bot_thread.start()
        config.bot_running = True
        return jsonify({"status": "started"})
    return jsonify({"status": "already running"})

@app.route('/stop-bot', methods=['POST'])
def stop_bot():
    config.bot_running = False
    return jsonify({"status": "stopped"})


@app.route('/bot-status')
def bot_status():
    return jsonify({"logs": bot_logs})

def run_flask():
    app.run(debug=True)