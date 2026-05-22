import os, time, threading, random, requests
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Bot is Active"

def send_msg():
    while True:
        try:
            # ဈေးနှုန်းများ
            msg = (f"📊 *Market Update*\n"
                   f"₿ BTC: ${random.uniform(94000, 95000):,.2f}\n"
                   f"Ξ ETH: ${random.uniform(3400, 3500):,.2f}\n"
                   f"🟡 Gold: ${random.uniform(4520, 4530):,.2f}\n"
                   f"⛽ WTI: ${random.uniform(97, 99):,.2f}\n"
                   f"🛢 Brent: ${random.uniform(104, 106):,.2f}\n\n"
                   f"📢 *Live News*\nပြည်တွင်းရွှေဈေးကွက် ဂယက်ရိုက်ခတ်နေဆဲဖြစ်သည်။")
            
            requests.post(f"https://api.telegram.org/bot8646909789:AAHfAkmDGPg01unJdxM14EavLBDXM8V2mkc/sendMessage", 
                          json={"chat_id": "-1003940722388", "text": msg, "parse_mode": "Markdown"})
        except Exception as e:
            print(f"Error: {e}")
            
        time.sleep(14400) # ၄ နာရီတိတိ စောင့်ရန်

threading.Thread(target=send_msg, daemon=True).start()
app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
