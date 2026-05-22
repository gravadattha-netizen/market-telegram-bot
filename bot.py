import os
import time
import requests
import threading
import random
from flask import Flask

app = Flask('')

# ======= [ TELEGRAM & VIBER CONFIG ] =======
TG_TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
TG_CHAT_ID = "-1003940722388"
VIBER_TOKEN = "515a44391e843e1d-c6a85536be62b3df-ef03348c4de8da51"
VIBER_CHAT_ID = "nVc17fiHk1a857P6swH9-a5WoImiKMxr"  # အစ်ကို့ Group ID အစစ်အမှန်

@app.route('/')
def home():
    return "Market Bot is running perfectly with Direct Push Mode!"

# ======= [ DATA POOL & GENERATOR ] =======
oil_news_pool = [
    "WTI နှင့် Brent Crude ရေနံစိမ်းဈေးကွက်တွင် ရောင်းလိုအား လိုချက်ကြောင့် ဈေးနှုန်းများ ပြန်လည်မြင့်တက်လှုပ်ခတ်လာသည်။",
    "နိုင်ငံတကာ စက်သုံးဆီဈေးကွက်အတွင်း အရောင်းအဝယ်အေးပြီး ရေနံစိမ်းပေါက်ဈေးနှုန်းများ ယနေ့တွင် အနည်းငယ် ပြန်လည်ကျဆင်းလာသည်။"
]
gold_news_pool = [
    "ကမ္ဘာ့ရွှေဈေးကွက်တွင် အမေရိကန်ဒေါ်လာဈေးနှုန်း အတက်အကျနှင့်အတူ ကမ္ဘာ့ရွှေရည်ညွှန်းဈေးနှုန်းများ မြင့်တက်လာသည်။",
    "ပြည်တွင်းပြည်ပ ရွှေဈေးကွက်အတွင်း ကမ္ဘာ့ရွှေပေါက်ဈေးနှုန်းများသည် လက်ရှိအချိန်တွင် ဂယက်ရိုက်ခတ်မှုများ ရှိနေသည်။"
]
crypto_news_pool = [
    "ကမ္ဘာ့ခရစ်တိုဈေးကွက်တွင် Bitcoin (BTC) နှင့် အခြားသော Altcoins များသည် လက်ရှိအချိန်တွင် အရောင်းအဝယ် ပြန်လည် အားကောင်းလာသည်။",
    "Bitcoin (BTC) ဈေးနှုန်း လှုပ်ခတ်မှုနှင့်အတူ ขရစ်တိုဈေးကွက်တစ်ခုလုံးတွင် ဝယ်လိုအား ပြန်လည်မြင့်တက်လျက်ရှိသည်။"
]

def generate_live_news():
    current_time = time.strftime("%I:%M %p", time.localtime(time.time() + 23400)) # Myanmar Time
    return f"• [{current_time} Live Update] {random.choice(oil_news_pool)}\n• [{current_time} Live Update] {random.choice(gold_news_pool)}\n• [{current_time} Live Update] {random.choice(crypto_news_pool)}"

def get_market_data():
    prices = {"BTC": "N/A", "ETH": "N/A", "SOL": "N/A", "GOLD": "N/A", "WTI": "N/A", "BRENT": "N/A"}
    timestamp = int(time.time())
    
    # 1. Crypto & Gold Data
    try:
        res = requests.get(f"https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,SOL,PAXG&tsyms=USD&_cb={timestamp}", timeout=8).json()
        if "BTC" in res:
            prices["BTC"] = f"${res['BTC']['USD']:,.2f}"
            prices["ETH"] = f"${res['ETH']['USD']:,.2f}"
            prices["SOL"] = f"${res['SOL']['USD']:,.2f}"
            prices["GOLD"] = f"${res['PAXG']['USD']:,.2f}"
    except: pass

    # 2. Oil Data (Twelvedata API)
    try:
        oil_url = f"https://api.twelvedata.com/price?symbol=WTI,BRENT&apikey=b3531fbefdf74de5b264e122b52b826b&_cb={timestamp}"
        oil_res = requests.get(oil_url, timeout=8).json()
        if "WTI" in oil_res and "price" in oil_res["WTI"]:
            prices["WTI"] = f"${float(oil_res['WTI']['price']):,.2f}"
        if "BRENT" in oil_res and "price" in oil_res["BRENT"]:
            prices["BRENT"] = f"${float(oil_res['BRENT']['price']):,.2f}"
    except: pass

    # API ကျသွားပါက ပြမည့် Default Values
    if prices["WTI"] == "N/A": prices["WTI"] = "$79.35"
    if prices["BRENT"] == "N/A": prices["BRENT"] = "$83.60"

    return prices

def generate_message_text(is_viber=False):
    prices = get_market_data()
    current_news = generate_live_news()
    b = "*" if is_viber else "**"
    return (
        f"🌟 {b}မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ{b} 🌟\n\n"
        f"📊 {b}Market Update{b}\n\n"
        f"₿ BTC: {prices['BTC']}\n"
        f"Ξ ETH: {prices['ETH']}\n"
        f"SOL: {prices['SOL']}\n"
        f"🟡 Gold (PAXG): {prices['GOLD']}\n"
        f"⛽ WTI Crude: {prices['WTI']}\n"
        f"🛢 Brent Crude: {prices['BRENT']}\n\n"
        f"📢 {b}သတင်းအချက်အလက်များ{b}\n"
        f"{current_news}\n\n"
        f"⚠️ _အရောင်းအဝယ်မပြုလုပ်ပါ သတင်းအချက်အလက် မျှဝေခြင်းပါ_"
    )

def send_update_to_all():
    print("Sending updates via Direct Push...")
    
    # ၁။ Telegram သို့ ပို့ခြင်း
    try:
        tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        tg_payload = {"chat_id": TG_CHAT_ID, "text": generate_message_text(is_viber=False), "parse_mode": "Markdown"}
        requests.post(tg_url, json=tg_payload, timeout=10)
        print("Telegram broadcast complete.")
    except Exception as e: print(f"TG Send Error: {e}")

    # ၂။ Viber Group သို့ တိုက်ရိုက်ပစ်ပို့ခြင်း (Viber Bot Webhook မလို၊ Group ထဲ အော်တိုရောက်မည့်စနစ်)
    try:
        viber_url = "https://chatapi.viber.com/pa/post"
        viber_payload = {
            "from": VIBER_CHAT_ID,
            "sender": {"name": "Market Live Report"},
            "type": "text",
            "text": generate_message_text(is_viber=True)
        }
        res = requests.post(viber_url, json=viber_payload, headers={"X-Viber-Auth-Token": VIBER_TOKEN}, timeout=10)
        print(f"Viber Direct Push Status: {res.status_code}")
    except Exception as e: print(f"Viber Send Error: {e}")

def auto_update_worker():
    time.sleep(3)
    send_update_to_all()
    while True:
        time.sleep(14400) # ၄ နာရီတစ်ခါ ပတ်မည်
        send_update_to_all()

if __name__ == "__main__":
    t_auto = threading.Thread(target=auto_update_worker)
    t_auto.daemon = True
    t_auto.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
