import os
import threading
import telebot
from flask import Flask, request, jsonify

app = Flask(__name__)
bot = telebot.TeleBot("8646909789:AAFhLamWEWkqjnCd2pfjEXn5lMoBWPCejNo")

# Global Cache
current_market_cache = {"last_update": "N/A"}

@app.route('/update', methods=['POST'])
def update_market_data():
    global current_market_cache
    data = request.get_json()
    print("n8n ကနေ ရောက်လာတဲ့ Data:", data)
    if data:
        current_market_cache.update(data)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == '__main__':
    # Flask ကို Background မှာ သီးသန့် Run ပါ
    threading.Thread(target=run_flask, daemon=True).start()
    # Bot ကိုတော့ Main Thread မှာ Polling လုပ်ပါ
    bot.polling(none_stop=True)
