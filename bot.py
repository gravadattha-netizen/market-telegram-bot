import os
import random
import requests
from flask import Flask

app = Flask(__name__)

TG_TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
TG_CHAT_ID = "-1003940722388"

@app.route('/send')
def trigger_send():
    # Binance API မှ တိုက်ရိုက်ယူခြင်း
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbols=[\"BTCUSDT\",\"ETHUSDT\"]", timeout=5)
        res = r.json()
        prices = {item['symbol']: f"${float(item['price']):,.2f}" for item in res}
    except:
        prices = {"BTCUSDT": "N/A", "ETHUSDT": "N/A"}
        
    msg = f"🚀 *Binance Live Market*\nBTC: {prices['BTCUSDT']}\nETH: {prices['ETHUSDT']}\n\n📢 *News Summary*\nဈေးကွက် အပြောင်းအလဲများ ဆက်လက်ရှိနေပါသည်။"
    
    requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                  json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    return "Message Sent!"

@app.route('/')
def home():
    return "Bot is Live!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
