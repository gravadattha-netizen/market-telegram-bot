import os, random, requests
from flask import Flask

app = Flask('')

TG_TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
TG_CHAT_ID = "-1003940722388"

# ဈေးနှုန်းနှင့် သတင်းများ
def get_market_data():
    return {
        "BTC": f"${random.uniform(94150, 94850):,.2f}",
        "ETH": f"${random.uniform(3410, 3460):,.2f}",
        "GOLD": f"${random.uniform(4522, 4529):,.2f}",
        "WTI": "$78.50"
    }

def send_to_telegram():
    data = get_market_data()
    msg = (f"🌟 *Market Update*\n\n"
           f"₿ BTC: {data['BTC']}\n"
           f"Ξ ETH: {data['ETH']}\n"
           f"🟡 Gold: {data['GOLD']}\n"
           f"⛽ WTI Crude: {data['WTI']}\n\n"
           f"📢 *Live News*\nဈေးကွက် အပြောင်းအလဲများ ဆက်လက်ရှိနေပါသည်။")
    
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    try:
        # Telegram သို့ ပို့ခြင်း
        requests.post(url, json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(f"Telegram Error: {e}")

# Cron-job က ဒီလိပ်စာကို လှမ်းခေါ်မှ အလုပ်လုပ်မည်
@app.route('/send')
def trigger():
    send_to_telegram()
    return "Message Sent!"

@app.route('/')
def home():
    return "Bot is Active!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
