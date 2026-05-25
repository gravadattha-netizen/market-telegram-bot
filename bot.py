import os
import random
import requests
from flask import Flask

app = Flask(__name__)

TG_TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
TG_CHAT_ID = "-1003940722388"

# Telegram သို့ စာပို့မည့် Function
def send_telegram_msg():
    prices = {
        "BTC": f"${random.uniform(94150, 94850):,.2f}",
        "ETH": f"${random.uniform(3410, 3460):,.2f}",
        "GOLD": f"${random.uniform(4522, 4529):,.2f}"
    }
    msg = f"🌟 Market Update\n\n₿ BTC: {prices['BTC']}\nΞ ETH: {prices['ETH']}\n🟡 Gold: {prices['GOLD']}\n\n📢 သတင်း: ဈေးကွက် အပြောင်းအလဲများ ဆက်လက်ရှိနေပါသည်။"
    
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "Markdown"})

# Cron-job က ဒီလိပ်စာကို ခေါ်မှ အလုပ်လုပ်မယ်
@app.route('/send')
def trigger_send():
    send_telegram_msg()
    return "Message Sent!"

@app.route('/')
def home():
    return "Bot is Active!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
