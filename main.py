from threading import Thread
from bot import run_bot
from web import run_flask

if __name__ == '__main__':
    Thread(target=run_bot).start()
    Thread(target=run_flask).start()
