import time
import requests
import threading
import os
import re
import xml.etree.ElementTree as ET
from flask import Flask, request, jsonify, render_template_string
import telebot
import google.generativeai as genai

# Configuration
TG_TOKEN = "8646909789:AAFhLamWEWkqjnCd2pfjEXn5lMoBWPCejNo"
GROUP_CHAT_ID = -1003940722388
GOOGLE_API_KEY = "AIzaSyAKM5IAugwBdKxrWQ__igkDwjwITW6f2kc"

genai.configure(api_key=GOOGLE_API_KEY)
app = Flask(__name__)
bot = telebot.TeleBot(TG_TOKEN)

# Global Data Cache
current_market_cache = {
    "prices": {"BTC": 0.0, "ETH": 0.0, "GOLD": 0.0, "WTI": 0.0, "BRENT": 0.0, "DXY": 0.0},
    "display_prices": {"BTC": "$0.00", "ETH": "$0.00", "GOLD": "$0.00", "WTI": "$0.00", "BRENT": "$0.00", "DXY": "0.00"},
    "trends": {"BTC": "neutral", "ETH": "neutral", "GOLD": "neutral", "WTI": "neutral", "BRENT": "neutral", "DXY": "neutral"},
    "last_update": "N/A",
    "crypto_gauge": 50, "wti_gauge": 50, "brent_gauge": 50, "gold_gauge": 50,
    "ai_news": "စနစ်စတင်ခြင်း...",
    "last_mops_text": "Waiting...",
    "admin_intel": "● QR စနစ်ဖြင့်တစ်နိုင်ငံလုံး ဆိုင်ပေါင်း ၁၇၃၀ တပ်ဆင်ရောင်းချ ပေးနေပါသည်"
}

# n8n က Data လက်ခံမယ့် Route (အသစ်ထည့်ထားသည်)
@app.route('/update', methods=['POST'])
def update_market_data():
    global current_market_cache
    data = request.get_json()
    if data:
        current_market_cache.update(data)
    return jsonify({"status": "success"}), 200

# Dashboard Route
@app.route('/')
def home():
    return render_template_string(DASHBOARD_HTML, data=current_market_cache)

# HTML Dashboard UI (သင်ပေးထားသော UI အဟောင်း)
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>⚡ Kyaw Gyi Market Intelligence Hub</title>
    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    <style>
        body { background-color: #0b0f19; color: #f1f5f9; font-family: sans-serif; padding: 20px; }
        .card { background: #111726; border-radius: 14px; padding: 16px; border: 1px solid #1e293b; margin-bottom: 10px; }
    </style>
</head>
<body>
    <h1>KYAW GYI INTELLIGENCE HUB ⚡</h1>
    <div class="card">Last Sync: {{ data.last_update }}</div>
    <div class="card">BTC: {{ data.display_prices.BTC }}</div>
    <div class="card">Admin Intel: {{ data.admin_intel }}</div>
</body>
</html>
"""

# Telegram & Logic
@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    if "ဈေး" in m.text:
        bot.reply_to(m, "Market data is updated via n8n.")

# Flask run thread
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.polling(none_stop=True)
