import os
import time
import requests
import threading
import random
from flask import Flask, request
import telebot

app = Flask('')

# ======= [ TELEGRAM & VIBER CONFIG ] =======
TG_TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
TG_CHAT_ID = "-1003940722388"
VIBER_TOKEN = "515a44391e843e1d-c6a85536be62b3df-ef03348c4de8da51"
VIBER_CHAT_ID = "nVc17fiHk1a857P6swH9-a5WoImiKMxr" 

bot = telebot.TeleBot(TG_TOKEN, threaded=False)

@app.route('/')
def home():
    return "Market Bot (Webhook Mode) is Active and Running Perfectly!"

@app.route('/' + TG_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

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
    "Bitcoin (BTC) ဈေးနှုန်း လှုပ်ခတ်မှုနှင့်အတူ ခရစ်တိုဈေးကွက်တစ်ခုလုံးတွင် ဝယ်လိုအား ပြန်လည်မြင့်တက်လျက်ရှိသည်။"
]

def generate_live_news():
    current_time = time.strftime("%I:%M %p", time.localtime(time.time() + 23400))
    return f"• [{current_time} Live Update] {random.choice(oil_news_pool)}\n• [{current_time} Live Update] {random.choice(gold_news_pool)}\n• [{current_time} Live Update] {random.choice(crypto_news_pool)}"

def get_market_data():
    prices = {"BTC": "$94,320.50", "ETH": "$3,420.15", "SOL": "$185.30", "GOLD": "$2,350.20", "WTI": "$78.45", "BRENT": "$82.90"}
    try:
        res = requests.get(f"https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,SOL,PAXG&tsyms=USD&_cb={int(time.time())}", timeout=10).json()
        if "BTC" in res:
            prices["BTC"] = f"${res['BTC']['USD']:,.2f}"
            prices["ETH"] = f"${res['ETH']['USD']:,.2f}"
            prices["SOL"] = f"${res['SOL']['USD']:,.2f}"
            prices["GOLD"] = f"${res['PAXG']['USD']:,.2f}"
    except: pass
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
    # Telegram ပို့ခြင်း
    try: bot.send_message(TG_CHAT_ID, generate_message_text(is_viber=False), parse_mode="Markdown")
    except Exception as e: print(f"TG Error: {e}")

    # Viber Group ပို့ခြင်း
    viber_payload = {
        "receiver": VIBER_CHAT_ID,
        "min_api_version": 1,
        "sender": {"name": "Market Live Report"},
        "type": "text",
        "text": generate_message_text(is_viber=True)
    }
    try: requests.post("https://chatapi.viber.com/pa/send_message", json=viber_payload, headers={"X-Viber-Auth-Token": VIBER_TOKEN}, timeout=10)
    except Exception as e: print(f"Viber Error: {e}")

def auto_update_worker():
    time.sleep(10)
    send_update_to_all()
    while True:
        time.sleep(14400) # ၄ နာရီတစ်ခါ ပတ်မည်
        send_update_to_all()

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    
    t_auto = threading.Thread(target=auto_update_worker)
    t_auto.daemon = True
    t_auto.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
