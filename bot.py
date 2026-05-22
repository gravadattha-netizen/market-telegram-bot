import os
import time
import threading
import random
from flask import Flask
import requests

app = Flask('')

TG_TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
TG_CHAT_ID = "-1003940722388"

# သတင်းများ
news = [
    "ကမ္ဘာ့ရွှေဈေးနှုန်း မြင့်တက်လာမှုကြောင့် ပြည်တွင်းရွှေဈေးကွက်တွင်လည်း လိုက်ပါလှုပ်ခတ်မှုများ ရှိနေကြောင်း သိရသည်။",
    "WTI နှင့် Brent Crude ရေနံစိမ်းဈေးကွက်တွင် ရောင်းလိုအား လိုချက်ကြောင့် ဈေးနှုန်းများ ပြန်လည်မြင့်တက်လှုပ်ခတ်လာသည်။",
    "ပြည်တွင်း စက်သုံးဆီဈေးနှုန်းများနှင့် သယ်ယူပို့ဆောင်ရေးစရိတ်များ ယနေ့တွင် အပြောင်းအလဲအချို့ ရှိနေကြောင်း သိရသည်။"
]

@app.route('/')
def home():
    return "Market Bot is Running."

def send_update():
    while True:
        try:
            # ဈေးနှုန်းများ
            btc = random.uniform(94000, 95000)
            eth = random.uniform(3400, 3500)
            gold = random.uniform(4520, 4530)
            
            msg = (f"🌟 *Market Update*\n\n"
                   f"₿ BTC: ${btc:,.2f}\n"
                   f"Ξ ETH: ${eth:,.2f}\n"
                   f"🟡 Gold: ${gold:,.2f}\n\n"
                   f"📢 *Live News*\n{random.choice(news)}")
            
            requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                          json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "Markdown"})
            
            print("Message Sent Successfully!")
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(14400) # 4 နာရီ

if __name__ == "__main__":
    # Thread ကို သီးသန့်စတင်ခြင်း
    threading.Thread(target=send_update, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
