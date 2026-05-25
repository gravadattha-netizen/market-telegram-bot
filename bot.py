import os
import time
import threading
import random
import requests
from flask import Flask

app = Flask('')

TG_TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
TG_CHAT_ID = "-1003940722388"

@app.route('/')
def home():
    return "2026 Ultimate Market Bot is Running!"

def get_market_data():
    return {
        "BTC": f"${random.uniform(94150, 94850):,.2f}",
        "ETH": f"${random.uniform(3410, 3460):,.2f}",
        "SOL": f"${random.uniform(183, 188):,.2f}",
        "GOLD": f"${random.uniform(4522, 4529):,.2f}",
        "WTI": f"${random.uniform(97, 98):,.2f}",
        "BRENT": f"${random.uniform(104, 105):,.2f}"
    }

def send_update_to_telegram():
    prices = get_market_data()
    msg = (f"🌟 *Market Update*\n\n"
           f"₿ BTC: {prices['BTC']}\n"
           f"Ξ ETH: {prices['ETH']}\n"
           f"💎 SOL: {prices['SOL']}\n"
           f"🟡 Gold: {prices['GOLD']}\n"
           f"⛽ WTI: {prices['WTI']}\n"
           f"🛢 Brent: {prices['BRENT']}\n\n"
           f"📢 *Live News*\n• နိုင်ငံတကာသတင်းများနှင့် ပြည်တွင်းဈေးကွက် အပြောင်းအလဲများ ဆက်လက်ရှိနေပါသည်။")
    
    try:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(f"Error: {e}")

# Cron Job သို့မဟုတ် UptimeRobot သုံးပါက ဒီ Route ကို ခေါ်ပါ
@app.route('/send')
def trigger_send():
    send_update_to_telegram()
    return "Message Sent!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
