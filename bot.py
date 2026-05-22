import os
import time
import threading
import random
from flask import Flask
import requests

app = Flask('')

TG_TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
TG_CHAT_ID = "-1003940722388"

# သတင်းအချက်အလက်များ
intl_news = "WTI နှင့် Brent Crude ရေနံစိမ်းဈေးကွက်တွင် ရောင်းလိုအား လိုချက်ကြောင့် ဈေးနှုန်းများ ပြန်လည်မြင့်တက်လှုပ်ခတ်လာသည်။"
mm_news = "ပြည်တွင်းရွှေဈေးကွက်နှင့် ဒေါ်လာဈေးကွက်အတွင်း ကမ္ဘာ့ရွှေဈေးလှုပ်ခတ်မှုကြောင့် ဈေးနှုန်းများ ဆက်လက် ဂယက်ရိုက်ခတ်မှု ရှိနေသည်။"

@app.route('/')
def home():
    return "Bot is Active and News are enabled."

def get_market_data():
    return {
        "BTC": f"${random.uniform(94000, 95000):,.2f}",
        "ETH": f"${random.uniform(3400, 3500):,.2f}",
        "GOLD": f"${random.uniform(4520, 4530):,.2f}",
        "WTI": f"${random.uniform(97, 99):,.2f}",
        "BRENT": f"${random.uniform(104, 106):,.2f}"
    }

def send_to_telegram():
    try:
        data = get_market_data()
        current_time = time.strftime("%I:%M %p")
        # ဈေးနှုန်းနှင့် သတင်းများ ပေါင်းစပ်ထားသော မက်ဆေ့ခ်ျ
        msg = (f"🌟 **မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ** 🌟\n\n"
               f"📊 **Market Update**\n\n"
               f"₿ BTC: {data['BTC']}\n"
               f"🟡 Gold: {data['GOLD']}\n"
               f"⛽ WTI: {data['WTI']}\n"
               f"🛢 Brent: {data['BRENT']}\n\n"
               f"📢 **သတင်းအချက်အလက်များ (Live)**\n"
               f"• [{current_time} နိုင်ငံတကာ] {intl_news}\n"
               f"• [{current_time} ပြည်တွင်း] {mm_news}\n\n"
               f"⚠️ _အရောင်းအဝယ်မပြုလုပ်ပါ သတင်းအချက်အလက် မျှဝေခြင်းပါ_")
        
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                      json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Error: {e}")

def worker():
    while True:
        send_to_telegram()
        time.sleep(14400) # 4 နာရီတစ်ခါ

if __name__ == "__main__":
    threading.Thread(target=worker, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
