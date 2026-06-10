import os
import threading
import telebot
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
TG_TOKEN = "8646909789:AAFhLamWEWkqjnCd2pfjEXn5lMoBWPCejNo"
bot = telebot.TeleBot(TG_TOKEN)

# Global Storage
current_market_cache = {"last_update": "N/A", "display_prices": {"BTC": "0"}, "admin_intel": "Loading..."}

@app.route('/update', methods=['POST'])
def update_market_data():
    global current_market_cache
    data = request.get_json()
    if data:
        current_market_cache = data
    return jsonify({"status": "success"}), 200

@app.route('/')
def home():
    return render_template_string("<h1>Data: {{ data }}</h1>", data=current_market_cache)

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    bot.polling(none_stop=True)
