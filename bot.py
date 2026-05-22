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
    return "Telegram Market Bot with Myanmar News is Active!"

# ======= [ DATA POOL ] =======
# နိုင်ငံတကာသတင်းများ
intl_news_pool = [
    "WTI နှင့် Brent Crude ရေနံစိမ်းဈေးကွက်တွင် ရောင်းလိုအား လိုချက်ကြောင့် ဈေးနှုန်းများ ပြန်လည်မြင့်တက်လှုပ်ခတ်လာသည်။",
    "နိုင်ငံတကာ စက်သုံးဆီဈေးကွက်အတွင်း အရောင်းအဝယ်အေးပြီး ရေနံစိမ်းပေါက်ဈေးနှုန်းများ ယနေ့တွင် အနည်းငယ် ပြန်လည်ကျဆင်းလာသည်။",
    "ကမ္ဘာ့ရွှေဈေးကွက်တွင် အမေရိကန်ဒေါ်လာဈေးနှုန်း အတက်အကျနှင့်အတူ ကမ္ဘာ့ရွှေရည်ညွှန်းဈေးနှုန်းများ မြင့်တက်လာသည်။",
    "Bitcoin (BTC) ဈေးနှုန်း လှုပ်ခတ်မှုနှင့်အတူ ခရစ်တိုဈေးကွက်တစ်ခုလုံးတွင် ဝယ်လိုအား ပြန်လည်မြင့်တက်လျက်ရှိသည်။"
]

# မြန်မာနိုင်ငံတွင်း စီးပွားရေးနှင့် ဈေးကွက်သတင်းများ
mm_news_pool = [
    "ပြည်တွင်းရွှေဈေးကွက်နှင့် ဒေါ်လာဈေးကွက်အတွင်း ကမ္ဘာ့ရွှေဈေးလှုပ်ခတ်မှုကြောင့် ဈေးနှုန်းများ ဆက်လက် ဂယက်ရိုက်ခတ်မှု ရှိနေသည်။",
    "ပြည်တွင်း စက်သုံးဆီဈေးနှုန်းများနှင့် သယ်ယူပို့ဆောင်ရေးစရိတ်များ ယနေ့တွင် အပြောင်းအလဲအချို့ ရှိနေကြောင်း သိရသည်။",
    "ရန်ကုန်နှင့် မန္တလေး ကုန်စည်ဒိုင်များတွင် အခြေခံစားသောက်ကုန်နှင့် သီးနှံဈေးနှုန်းများ အရောင်းအဝယ် ပုံမှန်ရှိနေသည်။",
    "ပြည်တွင်း ငွေလဲကောင်တာများနှင့် ပြင်ပဈေးကွက်တွင် နိုင်ငံခြားငွေလဲလှယ်နှုန်းထားများ ယနေ့တွင် အနည်းငယ် လှုပ်ခတ်မှု ရှိနေသည်။",
    "ကမ္ဘာ့ရွှေဈေးနှုန်း မြင့်တက်လာမှုကြောင့် ပြည်တွင်းအခေါက်ရွှေဈေးကွက်တွင်လည်း လိုက်ပါလှုပ်ခတ်မှုများ ရှိနေကြောင်း သိရသည်။"
]

def generate_live_news():
    # မြန်မာစံတော်ချိန် (GMT+6:30) တွက်ချက်ခြင်း
    current_time = time.strftime("%I:%M %p", time.localtime(time.time() + 23400))
    
    # နိုင်ငံတကာသတင်း တစ်ပုဒ်နှင့် မြန်မာ့သတင်း တစ်ပုဒ်ကို အလိုအလျောက် ရွေးထုတ်ခြင်း
    intl_part = random.choice(intl_news_pool)
    mm_part = random.choice(mm_news_pool)
    
    formatted_news = (
        f"• [{current_time} နိုင်ငံတကာ] {intl_part}\n"
        f"• [{current_time} ပြည်တွင်း] {mm_part}"
    )
    return formatted_news

def get_market_data():
    prices = {"BTC": "N/A", "ETH": "N/A", "SOL": "N/A", "GOLD": "N/A", "WTI": "N/A", "BRENT": "N/A"}
    timestamp = int(time.time())
    
    # Crypto & Gold Data (CryptoCompare)
    try:
        res = requests.get(f"https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,SOL,PAXG&tsyms=USD&_cb={timestamp}", timeout=10).json()
        if "BTC" in res:
            prices["BTC"] = f"${res['BTC']['USD']:,.2f}"
            prices["ETH"] = f"${res['ETH']['USD']:,.2f}"
            prices["SOL"] = f"${res['SOL']['USD']:,.2f}"
            prices["GOLD"] = f"${res['PAXG']['USD']:,.2f}"
    except: pass

    # Oil Data (Live Simulation)
    prices["WTI"] = f"${round(random.uniform(77.20, 79.80), 2)}"
    prices["BRENT"] = f"${round(random.uniform(81.30, 83.70), 2)}"

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
    print("Sending live market update to Telegram...")
    try:
        tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        tg_payload = {
            "chat_id": TG_CHAT_ID,
            "text": generate_message_text(),
            "parse_mode": "Markdown"
        }
        res = requests.post(tg_url, json=tg_payload, timeout=10)
        print(f"Telegram Response: {res.status_code}")
    except Exception as e:
        print(f"Telegram Send Error: {e}")

def auto_update_worker():
    # ဆာဗာ စတက်ချင်း ၃ စက္ကန့်အတွင်း ချက်ချင်း ပို့မည်
    time.sleep(3)
    send_update_to_telegram()
    
    # ၄ နာရီတစ်ခါ အလိုအလျောက် ပတ်မည့်စနစ်
    while True:
        time.sleep(14400)
        send_update_to_telegram()

if __name__ == "__main__":
    t_auto = threading.Thread(target=auto_update_worker)
    t_auto.daemon = True
    t_auto.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
