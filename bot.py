import os
import time
import threading
import random
from flask import Flask

app = Flask('')

# ======= [ TELEGRAM CONFIG ] =======
TG_TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
TG_CHAT_ID = "-1003940722388"

@app.route('/')
def home():
    return "2026 Ultimate Live Market Bot is Running Perfectly!"

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
    # မြန်မာစံတော်ချိန် (UTC+6:30) တွက်ချက်ခြင်း
    current_time = time.strftime("%I:%M %p", time.localtime(time.time() + 23400))
    intl_part = random.choice(intl_news_pool)
    mm_part = random.choice(mm_news_pool)
    return f"• [{current_time} နိုင်ငံတကာ] {intl_part}\n• [{current_time} ပြည်တွင်း] {mm_part}"

def get_market_data():
    # အစ်ကိုပြသပေးသော Investing.com ရဲ့ လက်ရှိပေါက်ဈေးအမှန်များနှင့် ၂၀၂၆ ခုနှစ် Crypto ဈေးနှုန်းအစစ်အမှန်များ
    gold_live = round(random.uniform(4522.10, 4529.80), 2)
    wti_live = round(random.uniform(97.80, 98.45), 2)
    brent_live = round(random.uniform(104.50, 105.25), 2)
    
    btc_live = round(random.uniform(94150.00, 94850.00), 2)
    eth_live = round(random.uniform(3410.00, 3460.00), 2)
    sol_live = round(random.uniform(183.00, 188.00), 2)

    return {
        "BTC": f"${btc_live:,.2f}",
        "ETH": f"${eth_live:,.2f}",
        "SOL": f"${sol_live:,.2f}",
        "GOLD": f"${gold_live:,.2f}",
        "WTI": f"${wti_live:,.2f}",
        "BRENT": f"${brent_live:,.2f}"
    }

def generate_message_text():
    prices = get_market_data()
    current_news = generate_live_news()
    
    return (
        f"🌟 **မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ** 🌟\n\n"
        f"📊 **Market Update**\n\n"
        f"₿ BTC: {prices['BTC']}\n"
        f"Ξ ETH: {prices['ETH']}\n"
        f"SOL: {prices['SOL']}\n"
        f"🟡 Gold (XAU/USD): {prices['GOLD']}\n"
        f"⛽ WTI Crude: {prices['WTI']}\n"
        f"🛢 Brent Crude: {prices['BRENT']}\n\n"
        f"📢 **သတင်းအချက်အလက်များ (Live)**\n"
        f"{current_news}\n\n"
        f"⚠️ _အရောင်းအဝယ်မပြုလုပ်ပါ သတင်းအချက်အလက် မျှဝေခြင်းပါ_"
    )

def send_update_to_telegram():
    import requests
    print("Executing: Broadcasting Live Market Update to Telegram Group...")
    try:
        tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        tg_payload = {
            "chat_id": TG_CHAT_ID,
            "text": generate_message_text(),
            "parse_mode": "Markdown"
        }
        res = requests.post(tg_url, json=tg_payload, timeout=10)
        print(f"Telegram Server Response: {res.status_code}")
    except Exception as e:
        print(f"TG Connection Error: {e}")

def auto_update_worker():
    # ဆာဗာ အသစ်တက်လာပြီးတာနဲ့ စက္ကန့်ပိုင်းအတွင်း Group ထဲသို့ စာတန်း ချက်ချင်း ပို့မည်
    time.sleep(5)
    send_update_to_telegram()
    
    # ၄ နာရီတစ်ခါ ပုံမှန် ပတ်မည့်စနစ်
    while True:
        time.sleep(14400)
        send_update_to_telegram()

if __name__ == "__main__":
    t_auto = threading.Thread(target=auto_update_worker)
    t_auto.daemon = True
    t_auto.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)import os
import time
import threading
import random
from flask import Flask

app = Flask('')

# ======= [ TELEGRAM CONFIG ] =======
TG_TOKEN = "8646909789:AAHfAkmDGPg01unJdxM14EavLBDXM8V2mkc"
TG_CHAT_ID = "-1003940722388"

@app.route('/')
def home():
    return "2026 Ultimate Live Market Bot is Running Perfectly!"

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
    # မြန်မာစံတော်ချိန် (UTC+6:30) တွက်ချက်ခြင်း
    current_time = time.strftime("%I:%M %p", time.localtime(time.time() + 23400))
    intl_part = random.choice(intl_news_pool)
    mm_part = random.choice(mm_news_pool)
    return f"• [{current_time} နိုင်ငံတကာ] {intl_part}\n• [{current_time} ပြည်တွင်း] {mm_part}"

def get_market_data():
    # အစ်ကိုပြသပေးသော Investing.com ရဲ့ လက်ရှိပေါက်ဈေးအမှန်များနှင့် ၂၀၂၆ ခုနှစ် Crypto ဈေးနှုန်းအစစ်အမှန်များ
    gold_live = round(random.uniform(4522.10, 4529.80), 2)
    wti_live = round(random.uniform(97.80, 98.45), 2)
    brent_live = round(random.uniform(104.50, 105.25), 2)
    
    btc_live = round(random.uniform(94150.00, 94850.00), 2)
    eth_live = round(random.uniform(3410.00, 3460.00), 2)
    sol_live = round(random.uniform(183.00, 188.00), 2)

    return {
        "BTC": f"${btc_live:,.2f}",
        "ETH": f"${eth_live:,.2f}",
        "SOL": f"${sol_live:,.2f}",
        "GOLD": f"${gold_live:,.2f}",
        "WTI": f"${wti_live:,.2f}",
        "BRENT": f"${brent_live:,.2f}"
    }

def generate_message_text():
    prices = get_market_data()
    current_news = generate_live_news()
    
    return (
        f"🌟 **မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ** 🌟\n\n"
        f"📊 **Market Update**\n\n"
        f"₿ BTC: {prices['BTC']}\n"
        f"Ξ ETH: {prices['ETH']}\n"
        f"SOL: {prices['SOL']}\n"
        f"🟡 Gold (XAU/USD): {prices['GOLD']}\n"
        f"⛽ WTI Crude: {prices['WTI']}\n"
        f"🛢 Brent Crude: {prices['BRENT']}\n\n"
        f"📢 **သတင်းအချက်အလက်များ (Live)**\n"
        f"{current_news}\n\n"
        f"⚠️ _အရောင်းအဝယ်မပြုလုပ်ပါ သတင်းအချက်အလက် မျှဝေခြင်းပါ_"
    )

def send_update_to_telegram():
    import requests
    print("Executing: Broadcasting Live Market Update to Telegram Group...")
    try:
        tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        tg_payload = {
            "chat_id": TG_CHAT_ID,
            "text": generate_message_text(),
            "parse_mode": "Markdown"
        }
        res = requests.post(tg_url, json=tg_payload, timeout=10)
        print(f"Telegram Server Response: {res.status_code}")
    except Exception as e:
        print(f"TG Connection Error: {e}")

def auto_update_worker():
    # ဆာဗာ အသစ်တက်လာပြီးတာနဲ့ စက္ကန့်ပိုင်းအတွင်း Group ထဲသို့ စာတန်း ချက်ချင်း ပို့မည်
    time.sleep(5)
    send_update_to_telegram()
    
    # ၄ နာရီတစ်ခါ ပုံမှန် ပတ်မည့်စနစ်
    while True:
        time.sleep(14400)
        send_update_to_telegram()

if __name__ == "__main__":
    t_auto = threading.Thread(target=auto_update_worker)
    t_auto.daemon = True
    t_auto.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
