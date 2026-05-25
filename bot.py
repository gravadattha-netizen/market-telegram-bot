import os, time, random, requests
from flask import Flask

app = Flask('')

TG_TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
TG_CHAT_ID = "-1003940722388"

# ဈေးနှုန်းနှင့် သတင်းများ
def get_market_data():
    return {
        "BTC": f"${random.uniform(94150, 94850):,.2f}",
        "ETH": f"${random.uniform(3410, 3460):,.2f}",
        "GOLD": f"${random.uniform(4522, 4529):,.2f}"
    }

def send_to_telegram():
    data = get_market_data()
    msg = f"🌟 Market Update\n\n₿ BTC: {data['BTC']}\nΞ ETH: {data['ETH']}\n🟡 Gold: {data['GOLD']}\n\n📢 သတင်း: ဈေးကွက် အပြောင်းအလဲများ ဆက်ရှိနေသည်။"
    requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                  json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "Markdown"})

@app.route('/send') # အရေးကြီးဆုံး: ဒီ Route ရှိမှ Cron Job အလုပ်လုပ်မယ်
def trigger():
    send_to_telegram()
    return "Message Sent!"

@app.route('/')
def home():
    return "Bot is Active!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
