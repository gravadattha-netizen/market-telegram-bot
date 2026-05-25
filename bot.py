import os, time, random, requests
from flask import Flask

app = Flask('')

TG_TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
TG_CHAT_ID = "-1003940722388"

def send_update_to_telegram():
    # ဈေးနှုန်းများ (Live data ပုံစံဖြင့်)
    prices = {
        "BTC": f"${random.uniform(94150, 94850):,.2f}",
        "ETH": f"${random.uniform(3410, 3460):,.2f}",
        "GOLD": f"${random.uniform(4522, 4529):,.2f}"
    }
    msg = f"🌟 Market Update\n\n₿ BTC: {prices['BTC']}\nΞ ETH: {prices['ETH']}\n🟡 Gold: {prices['GOLD']}\n\n📢 သတင်းများ: ဈေးကွက် အပြောင်းအလဲများ ဆက်လက်ရှိနေပါသည်။"
    
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TG_CHAT_ID, "text": msg}, timeout=10)

@app.route('/send')
def trigger():
    send_update_to_telegram()
    return "Message Sent Successfully"

@app.route('/')
def home():
    return "Bot is Active"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
