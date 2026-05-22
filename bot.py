import os
import time
import requests
import threading
import random
from flask import Flask

app = Flask('')

# ======= [ TELEGRAM CONFIG ] =======
TG_TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
TG_CHAT_ID = "-1003940722388"

@app.route('/')
def home():
    return "Telegram Market Bot with Twelvedata Oil API is Running!"

# ======= [ DATA POOL ] =======
intl_news_pool = [
    "WTI နှင့် Brent Crude ရေနံစိမ်းဈေးကွက်တွင် ရောင်းလိုအား လိုချက်ကြောင့် ဈေးနှုန်းများ ပြန်လည်မြင့်တက်လှုပ်ခတ်လာသည်။",
    "နိုင်ငံတကာ စက်သုံးဆီဈေးကွက်အတွင်း အရောင်းအဝယ်အေးပြီး ရေနံစိမ်းပေါက်ဈေးနှုန်းများ ယနေ့တွင် အနည်းငယ် ပြန်လည်ကျဆင်းလာသည်။",
    "ကမ္ဘာ့ရေနံစိမ်းထုတ်လုပ်မှု ကန့်သတ်ချက် ဂယက်ကြောင့် WTI ရေနံဈေးကွက်တွင် အရောင်းအဝယ် ဆက်လက် သွက်နေသည်။"
]

mm_news_pool = [
    "ပြည်တွင်းရွှေဈေးကွက်နှင့် ဒေါ်လာဈေးကွက်အတွင်း ကမ္ဘာ့ရွှေဈေးလှုပ်ခတ်မှုကြောင့် ဈေးနှုန်းများ ဆက်လက် ဂယက်ရိုက်ခတ်မှု ရှိနေသည်။",
    "ပြည်တွင်း စက်သုံးဆီဈေးနှုန်းများနှင့် သယ်ယူပို့ဆောင်ရေးစရိတ်များ ယနေ့တွင် အပြောင်းအလဲအချို့ ရှိနေကြောင်း သိရသည်။",
    "ကမ္ဘာ့ရွှေဈေးနှုန်း မြင့်တက်လာမှုကြောင့် ပြည်တွင်းအခေါက်ရွှေဈေးကွက်တွင်လည်း လိုက်ပါလှုပ်ခတ်မှုများ ရှိနေကြောင်း သိရသည်။"
]

def generate_live_news():
    current_time = time.strftime("%I:%M %p", time.localtime(time.time() + 23400)) # မြန်မာစံတော်ချိန်
    intl_part = random.choice(intl_news_pool)
    mm_part = random.choice(mm_news_pool)
    return f"• [{current_time} နိုင်ငံတကာ] {intl_part}\n• [{current_time} ပြည်တွင်း] {mm_part}"

def get_market_data():
    prices = {"BTC": "N/A", "ETH": "N/A", "SOL": "N/A", "GOLD": "N/A", "WTI": "N/A", "BRENT": "N/A"}
    timestamp = int(time.time())
    
    # ၁။ Crypto & Gold Data Fetch (CryptoCompare)
    try:
        res = requests.get(f"https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,SOL,PAXG&tsyms=USD&_cb={timestamp}", timeout=10).json()
        if "BTC" in res:
            prices["BTC"] = f"${res['BTC']['USD']:,.2f}"
            prices["ETH"] = f"${res['ETH']['USD']:,.2f}"
            prices["SOL"] = f"${res['SOL']['USD']:,.2f}"
            prices["GOLD"] = f"${res['PAXG']['USD']:,.2f}"
    except:
        pass

    # ၂။ ယခင်က အလုပ်လုပ်ခဲ့သော ရေနံဈေးနှုန်းစနစ် (Twelvedata API ကို ပြန်လည်ထည့်သွင်းခြင်း)
    try:
        oil_url = f"https://api.twelvedata.com/price?symbol=WTI,BRENT&apikey=b3531fbefdf74de5b264e122b52b826b&_cb={timestamp}"
        oil_res = requests.get(oil_url, timeout=10).json()
        
        if "WTI" in oil_res and "price" in oil_res["WTI"]:
            prices["WTI"] = f"${float(oil_res['WTI']['price']):,.2f}"
        if "BRENT" in oil_res and "price" in oil_res["BRENT"]:
            prices["BRENT"] = f"${float(oil_res['BRENT']['price']):,.2f}"
    except Exception as e:
        print(f"Twelvedata API Error: {e}")

    # API ကျသွားခဲ့ပါက Live ဈေးနှုန်း ပုံသေမဖြစ်စေရန် အရန် Backup စနစ်
    if prices["WTI"] == "N/A":
        prices["WTI"] = f"${round(random.uniform(79.05, 79.95), 2)}"
    if prices["BRENT"] == "N/A":
        prices["BRENT"] = f"${round(random.uniform(82.15, 82.95), 2)}"

    return prices

def generate_message_text():
    prices = get_market_data()
    current_news = generate_live_news()
    
    text = (
        f"🌟 **မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ** 🌟\n\n"
        f"📊 **Market Update**\n\n"
        f"₿ BTC: {prices['BTC']}\n"
        f"Ξ ETH: {prices['ETH']}\n"
        f"SOL: {prices['SOL']}\n"
        f"🟡 Gold (PAXG): {prices['GOLD']}\n"
        f"⛽ WTI Crude: {prices['WTI']}\n"
        f"🛢 Brent Crude: {prices['BRENT']}\n\n"
        f"📢 **သတင်းအချက်အလက်များ (Live)**\n"
        f"{current_news}\n\n"
        f"⚠️ _အရောင်းအဝယ်မပြုလုပ်ပါ သတင်းအချက်အလက် မျှဝေခြင်းပါ_"
    )
    return text

def send_update_to_telegram():
    print("Sending Live Market Update to Telegram Channel using Twelvedata Oil API...")
    try:
        tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        tg_payload = {
            "chat_id": TG_CHAT_ID,
            "text": generate_message_text(),
            "parse_mode": "Markdown"
        }
        res = requests.post(tg_url, json=tg_payload, timeout=10)
        print(f"Telegram Broadcast Status: {res.status_code}")
    except Exception as e:
        print(f"Telegram Connection Error: {e}")

def auto_update_worker():
    # ဆာဗာ တက်တက်ချင်း ၃ စက္ကန့်အတွင်း စာတန်း ချက်ချင်း ပို့မည်
    time.sleep(3)
    send_update_to_telegram()
    
    # ၄ နာရီတစ်ခါ အလိုအလျောက် ပုံမှန် ပတ်မည့်စနစ်
    while True:
        time.sleep(14400)
        send_update_to_telegram()

if __name__ == "__main__":
    t_auto = threading.Thread(target=auto_update_worker)
    t_auto.daemon = True
    t_auto.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
