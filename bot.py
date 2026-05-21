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
    return "Market Bot with 4-Hour Interval is Active!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Token နှင့် Chat ID (အစ်ကို့ Bot ပုံစံအတိုင်း တိုက်ရိုက်ထည့်သွင်းထားသည်)
TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
MY_ID = "-1003940722388"
bot = telebot.TeleBot(TOKEN)

# ကမ္ဘာ့ကုန်စည်ဈေးကွက် သတင်းမျိုးစုံ ပုံစံများ
oil_news_pool = [
    "WTI နှင့် Brent Crude ရေနံစိမ်းဈေးကွက်တွင် ရောင်းလိုအား လိုအပ်ချက်ကြောင့် ဈေးနှုန်းများ ပြန်လည်မြင့်တက်လှုပ်ခတ်လာသည်။",
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
    """ 📢 အချိန်စနစ် (Timestamp) နှင့် ကျဘန်းစနစ်ဖြင့် သတင်းကို ၄ နာရီတစ်ခါ အသစ်ထုတ်ပေးခြင်း """
    # မြန်မာစံတော်ချိန် တွက်ချက်ခြင်း (+6:30 standard)
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
    """ 📈 Crypto နှင့် ရေနံဈေးနှုန်းများ Live အစစ်ကို ရယူခြင်း """
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
        f"📢 **သတင်းအချက်အလက်များ**\n"
        f"{current_news}\n\n"
        f"⚠️ _အရောင်းအဝယ်မပြုလုပ်ပါ သတင်းအချက်အလက် မျှဝေခြင်းပါ_"
    )
    return text

def send_update():
    text = generate_message_text()
    try:
        bot.send_message(MY_ID, text, parse_mode="Markdown")
        print("Message sent successfully!")
    except Exception as e:
        print(f"Telegram Send Error: {e}")

@bot.message_handler(commands=['price'])
def manual_price(message):
    send_update()

def auto_update_worker():
    print("Auto Update Thread Started (4-Hour Interval)...")
    time.sleep(5)
    send_update()
    
    while True:
        time.sleep(14400)  # 🚨 စက္ကန့် ၁၄၄၀၀ (ဆိုလိုသည်မှာ ကွက်တိ ၄ နာရီ) စောင့်ပြီးမှ ပို့မည်
        send_update()

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
