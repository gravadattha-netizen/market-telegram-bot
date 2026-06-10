import os
import threading
import telebot
from flask import Flask, request, jsonify

app = Flask(__name__)
bot = telebot.TeleBot("8646909789:AAFhLamWEWkqjnCd2pfjEXn5lMoBWPCejNo")

# Data Cache
current_market_cache = {"status": "Waiting for n8n"}

@app.route('/update', methods=['POST'])
def update():
    global current_market_cache
    data = request.get_json()
    if data:
        current_market_cache.update(data)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == '__main__':
    # Flask ကို Thread နဲ့ run
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Bot ကို infinity_polling သုံးပြီး none_stop=False ထားပါ
    bot.infinity_polling(none_stop=False)
