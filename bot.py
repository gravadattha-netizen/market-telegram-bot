import os
import threading
import telebot
from flask import Flask, request, jsonify

app = Flask(__name__)
bot = telebot.TeleBot("8646909789:AAFhLamWEWkqjnCd2pfjEXn5lMoBWPCejNo")

# Global Cache
market_data = {"status": "Waiting for data"}

@app.route('/update', methods=['POST'])
def update():
    global market_data
    market_data = request.get_json()
    return jsonify({"status": "success"}), 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    bot.polling(none_stop=True)
