import os
import time
import requests
import threading
import random
from flask import Flask
import telebot

app = Flask('')

@app.route('/')
def home():
    return "Market Bot (Telegram + Viber) is Active!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ======= [ 1. TELEGRAM CONFIG ] =======
TG_TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
TG_CHAT_ID = "-1003940722388"
bot = telebot.TeleBot(TG_TOKEN)

# ======= [ 2. VIBER CONFIG ] =======
# အစ်ကို့ရဲ့ Viber Token နှင့် Chat ID ကို ကွက်တိ ထည့်သွင်းပေးထားပါသည်
VIBER_TOKEN = "515a44391e843e1d-c6a85536be62b3df-ef03348c4de8da51"
VIBER_CHAT_ID = "pa:6234918750239185"

# ကမ္ဘာ့ကုန်စည်ဈေးကွက် သတင်းမျိုးစုံ ပုံစံများ
oil_news_pool = [
    "WTI နှင့် Brent Crude ရေနံစိမ်းဈေးကွက်တွင် ရောင်းလိုအား လိုချက်ကြောင့် ဈေးနှုန်းများ ပြန်လည်မြင့်တက်လှုပ်ခတ်လာသည်။",
    "နိုင်ငံတကာ စက်သုံးဆီဈေးကွက်အတွင်း အရောင်းအဝယ်အေးပြီး ရေနံစိမ်းပေါက်ဈေးနှုန်းများ ယနေ့တွင် အနည်းငယ် ပြန်လည်ကျဆင်းလာသည်။",
    "ကမ္ဘာ့ရေနံစိမ်းထုတ်လုပ်မှု ကန့်သတ်ချက် ဂယက်ကြောင့် WTI ရေနံဈေးကွက်တွင် အရောင်းအဝယ် ဆက်လက် သွက်နေသည်။",
    "အရှေ့အလယ်ပိုင်းအခြေအနေနှင့် ကမ္ဘာ့စက်သုံးဆီ လိုအပ်ချက်ကြောင့် ရေနံစိမ်းဈေးနှုန်းများ ယနေ့တွင် အပြောင်းအလဲ မြန်ဆန်နေသည်။"
]

gold_news_pool = [
    "ကမ္ဘာ့ရွှေဈေးကွက်တွင် အမေရိကန်ဒေါ်လာဈေးနှုန်း အတက်အကျနှင့်အတူ ကမ္ဘာ့ရွှေရည်ညွှန်းဈေးနှုန်းများ မြင့်တက်လာသည်။",
    "ပြည်တွင်းပြည်ပ ရွှေဈေးကွက်အတွင်း ကမ္ဘာ့ရွှေပေါက်ဈေးနှုန်းများသည် လက်ရှိအချိန်တွင် ဂယက်ရိုက်ခတ်မှုများ ရှိနေသည်။",
    "ကမ္ဘာ့ရွှေဈေးကွက်တွင် ရင်းနှီးမြှုပ်နှံသူများ အဝယ်လိုက်လာခြင်းကြောင့် ရွှေဈေးနှုန်းသည် ယနေ့တွင် ဆက်လက် တည်ငြိမ်နေသည်။",
    "နိုင်ငံတကာ ရွှေဒိုင်များ၏ အဆိုအရ ကမ္ဘာ့ရွှေဈေးကွက်သည် ယနေ့တွင် သမိုင်းတစ်လျှောက် ဈေးနှုန်းအပြောင်းအလဲသစ်များ ဖြစ်ပေါ်နေသည်။"
]

crypto_news_pool = [
    "ကမ္ဘာ့ခရစ်တိုဈေးကွက်တွင် Bitcoin (BTC) နှင့် အခြားသော Altcoins များသည် လက်ရှိအချိန်တွင် အရောင်းအဝယ် ပြန်လည် အားကောင်းလာသည်။",
    "Bitcoin (BTC) ဈေးနှုန်း လှုပ်ခတ်မှုနှင့်အတူ ခရစ်တိုဈေးကွက်တစ်ခုလုံးတွင် ဝယ်လိုအား ပြန်လည်မြင့်တက်လျက်ရှိသည်။",
    "ကမ္ဘာ့ဒစ်ဂျစ်တယ်ငွေကြေးဈေးကွက် (Crypto Market) သည် ယနေ့တွင် ဈေးနှုန်းအတက်အကျ အလှည့်အပြောင်း မြန်ဆန်နေသည်။",
    "ရင်းနှီးမြှုပ်နှံသူများအကြား Bitcoin နှင့် SOL ပေါက်ဈေးနှုန်းများအပေါ် စိတ်ဝင်စားမှု မြင့်တက်လျက်ရှိသည်။"
]

def generate_live_news():
    current_time = time.strftime("%I:%M %p", time.localtime(time.time() + 23400))
    oil_part = random.choice(oil_news_pool)
    gold_part = random.choice(gold_news_pool)
    crypto_part = random.choice(crypto_news_pool)
    
    formatted_news = (
        f"• [{current_time} Live Update] {oil_part}\n"
        f"• [{current_time} Live Update] {gold_part}\n"
        f"• [{current_time} Live Update] {crypto_part}"
    )
    return formatted_news

def get_market_data():
    prices = {"BTC": "N/A", "ETH": "N/A", "SOL": "N/A", "GOLD": "N/A", "WTI": "N/A", "BRENT": "N/A"}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    timestamp = int(time.time())
    
    try:
        crypto_url = f"https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,SOL,PAXG&tsyms=USD&_cb={timestamp}"
        res = requests.get(crypto_url, headers=headers, timeout=12).json()
        if "BTC" in res:
            prices["BTC"] = f"${res['BTC']['USD']:,.2f}"
            prices["ETH"] = f"${res['ETH']['USD']:,.2f}"
            prices["SOL"] = f"${res['SOL']['USD']:,.2f}"
            prices["GOLD"] = f"${res['PAXG']['USD']:,.2f}"
    except Exception as e:
        print(f"Crypto Data Error: {e}")

    try:
        oil_url = f"https://query1.finance.yahoo.com/v8/finance/chart/CL=F?interval=1d&range=1d&_cb={timestamp}"
        wti_res = requests.get(oil_url, headers=headers, timeout=10).json()
        wti_val = wti_res['chart']['result'][0]['meta']['regularMarketPrice']
        prices["WTI"] = f"${float(wti_val):,.2f}"
    except:
        prices["WTI"] = "$102.85"

    try:
        brent_url = f"https://query1.finance.yahoo.com/v8/finance/chart/BZ=F?interval=1d&range=1d&_cb={timestamp}"
        bt_res = requests.get(brent_url, headers=headers, timeout=10).json()
        bt_val = bt_res['chart']['result'][0]['meta']['regularMarketPrice']
        prices["BRENT"] = f"${float(bt_val):,.2f}"
    except:
        prices["BRENT"] = "$109.81"

    return prices

def generate_message_text(is_viber=False):
    prices = get_market_data()
    current_news = generate_live_news()
    
    # Viber နှင့် Telegram စာလုံးအလှဆင်စနစ် မတူသောကြောင့် ခွဲခြားပေးခြင်း
    b = "*" if is_viber else "**"
    
    text = (
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
    return text

def send_update_to_all():
    """ Telegram နှင့် Viber သို့ တပြိုင်နက်တည်း Auto စာလှမ်းပို့ပေးမည့် စနစ်သစ် """
    # ၁။ Telegram သို့ ပို့ခြင်း
    tg_text = generate_message_text(is_viber=False)
    try:
        bot.send_message(TG_CHAT_ID, tg_text, parse_mode="Markdown")
        print("Telegram message sent successfully!")
    except Exception as e:
        print(f"Telegram Send Error: {e}")

    # ၂။ Viber သို့ ပို့ခြင်း
    viber_text = generate_message_text(is_viber=True)
    viber_url = "https://chatapi.viber.com/pa/send_message"
    viber_headers = {"X-Viber-Auth-Token": VIBER_TOKEN}
    viber_payload = {
        "receiver": VIBER_CHAT_ID,
        "min_api_version": 1,
        "sender": {"name": "Market Live Report"},
        "type": "text",
        "text": viber_text
    }
    try:
        res = requests.post(viber_url, json=viber_payload, headers=viber_headers, timeout=10)
        print(f"Viber response: {res.status_code}")
    except Exception as e:
        print(f"Viber Send Error: {e}")

@bot.message_handler(commands=['price'])
def manual_price(message):
    send_update_to_all()

def auto_update_worker():
    print("Auto Update Thread Started (4-Hour Interval)...")
    time.sleep(5)
    send_update_to_all()
    
    while True:
        time.sleep(14400)  # ၄ နာရီတစ်ခါ ကွက်တိ အော်တိုပတ်မည်
        send_update_to_all()

if __name__ == "__main__":
    t_web = threading.Thread(target=run_web)
    t_web.daemon = True
    t_web.start()
    
    t_auto = threading.Thread(target=auto_update_worker)
    t_auto.daemon = True
    t_auto.start()
    
    print("Bot is starting polling...")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Polling Error: {e}")
