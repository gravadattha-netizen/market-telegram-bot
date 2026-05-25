import os
import random
import requests
from flask import Flask

app = Flask(__name__)

# 🚨 TOKEN နှင့် CHAT_ID ကို အမှန်ကန်ဆုံး ပြန်ပြင်ပေးထားပါတယ်
TG_TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
TG_CHAT_ID = -1001940722388  # Chat ID အမှန်ကို ပြန်ပြောင်းထားသည်

@app.route('/send')
def trigger_send():
    prices = {
        "BTC": f"${random.uniform(94150, 94850):,.2f}",
        "ETH": f"${random.uniform(3410, 3460):,.2f}",
        "GOLD": f"${random.uniform(4522, 4529):,.2f}"
    }
    
    # Markdown အစား စိတ်အချရဆုံး HTML Format ပြောင်းလဲထားပါသည်
    msg = (
        "🌟 <b>Market Update</b>\n\n"
        "₿ <b>BTC:</b> <code>" + prices['BTC'] + "</code>\n"
        "Ξ <b>ETH:</b> <code>" + prices['ETH'] + "</code>\n"
        "🟡 <b>Gold:</b> <code>" + prices['GOLD'] + "</code>\n\n"
        "📢 သတင်း: ဈေးကွက် အပြောင်းအလဲများ ဆက်လက်ရှိနေပါသည်။"
    )
    
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"  # HTML သုံးထား၍ Error လုံးဝမတက်ပါ
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return "Message Sent Successfully to Telegram!"
        else:
            return f"Telegram API Error: {response.text}", response.status_code
    except Exception as e:
        return f"Network Error: {str(e)}", 500

@app.route('/')
def home():
    return "Bot is Active and Ready!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
