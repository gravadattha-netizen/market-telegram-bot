import os
import requests
from flask import Flask

app = Flask(__name__)

TG_TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
TG_CHAT_ID = "-1003940722388"

@app.route('/send')
def trigger_send():
    # ၁။ Binance မှ Live စျေးနှုန်းယူခြင်း
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbols=[\"BTCUSDT\",\"ETHUSDT\",\"SOLUSDT\"]", timeout=10)
        data = r.json()
        prices = {item['symbol']: f"${float(item['price']):,.2f}" for item in data}
    except:
        prices = {"BTCUSDT": "N/A", "ETHUSDT": "N/A", "SOLUSDT": "N/A"}

    # ၂။ သတင်းအနှစ်ချုပ် (Crypto သတင်းများ)
    news = ("📢 *Live Market News Update*\n"
            "• BTC: စျေးကွက်တွင် အတက်အကျများ ဆက်လက်ဖြစ်ပေါ်နေသည်။\n"
            "• ETH: အရောင်းအဝယ်ပမာဏ တည်ငြိမ်နေသည်။\n"
            "• SOL: အဓိက Support အဆင့်တွင် ထိန်းထားနိုင်သည်။")
            
    msg = (f"🚀 *Binance Live Price*\n"
           f"₿ BTC: {prices.get('BTCUSDT', 'N/A')}\n"
           f"Ξ ETH: {prices.get('ETHUSDT', 'N/A')}\n"
           f"◈ SOL: {prices.get('SOLUSDT', 'N/A')}\n\n{news}")
    
    requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                  json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    return "Message Sent!"

@app.route('/')
def home():
    return "Bot is Live and Fetching Data!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
