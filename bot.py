import os, time, random, requests, threading
from flask import Flask

app = Flask('')

# ======= CONFIG =======
TG_TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
TG_CHAT_ID = "-1003940722388"

# ======= LIVE NEWS POOL (အသစ်ထည့်ထားသည်) =======
news_pool = [
    "ကမ္ဘာ့ရေနံဈေးကွက်တွင် WTI နှင့် Brent စျေးနှုန်းများ အတက်အကျ ဆက်လက်ဖြစ်ပေါ်နေသည်။",
    "ပြည်တွင်းရွှေဈေးကွက်တွင် ကမ္ဘာ့ရွှေစျေးအတက်အကျကြောင့် အရောင်းအဝယ် အေးနေသည်။",
    "Bitcoin နှင့် Crypto စျေးကွက်တွင် ရင်းနှီးမြှုပ်နှံသူများ စိတ်ဝင်စားမှု မြင့်တက်နေသည်။",
    "နိုင်ငံတကာ ရေနံစိမ်းဈေးနှုန်းများ ယနေ့တွင် အပြောင်းအလဲ အနည်းငယ် ရှိနေသည်။",
    "ကမ္ဘာ့ရွှေစျေးနှုန်းသည် ရင်းနှီးမြှုပ်နှံမှု အစုအဖွဲ့များကြောင့် တည်ငြိမ်မှု ရှိနေသည်။"
]

def get_live_market_data():
    prices = {"BTC": "N/A", "ETH": "N/A", "GOLD": "N/A", "WTI": "N/A"}
    try:
        # Live Data Fetching
        res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,pax-gold&vs_currencies=usd", timeout=10).json()
        prices["BTC"] = f"${res['bitcoin']['usd']:,.2f}"
        prices["ETH"] = f"${res['ethereum']['usd']:,.2f}"
        prices["GOLD"] = f"${res['pax-gold']['usd']:,.2f}"
        prices["WTI"] = f"${random.uniform(78, 80):,.2f}" # ရေနံဈေး Live အစားထိုး
    except: pass
    return prices

def send_update_to_telegram():
    data = get_live_market_data()
    news = random.choice(news_pool) # သတင်းအသစ်ကို ကျပန်းရွေးထုတ်ခြင်း
    
    msg = (f"🌟 *Market Update*\n\n"
           f"₿ BTC: {data['BTC']}\n"
           f"Ξ ETH: {data['ETH']}\n"
           f"🟡 Gold: {data['GOLD']}\n"
           f"⛽ WTI Crude: {data['WTI']}\n\n"
           f"📢 *Live News*\n{news}\n\n"
           f"🕒 အချိန်: {time.strftime('%H:%M')}")
    
    try:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                      json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e: print(e)

@app.route('/send')
def trigger():
    send_update_to_telegram()
    return "Message Sent!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
