import os
import threading
import telebot
from flask import Flask, request, jsonify

# 1. Setup App
app = Flask(__name__)
bot = telebot.TeleBot("8646909789:AAFhLamWEWkqjnCd2pfjEXn5lMoBWPCejNo")

# 2. Memory (Data Storage)
market_data = {"status": "Waiting for data from n8n"}

# 3. Route for n8n (HTTP Request)
@app.route('/update', methods=['POST'])
def update():
    global market_data
    data = request.get_json()
    if data:
        market_data = data
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "no data"}), 400

# 4. Web Server Logic
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

# 5. Main Execution
if __name__ == '__main__':
    # Start Flask in background
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Start Bot
    bot.polling(none_stop=True)
