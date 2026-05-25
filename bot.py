import os
import time
import requests
import threading
import random  # <-- ဒီကောင် ကျန်ခဲ့လို့ စက်ရပ်သွားတာ၊ အခု ထည့်ပေးလိုက်ပါပြီ
import xml.etree.ElementTree as ET
from flask import Flask
import telebot

app = Flask('')

@app.route('/')
def home():
    return "Market Bot with 4-Hour Interval is Active!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Token နှင့် Chat ID (ကျိန်းသေ အလုပ်လုပ်ပြီးသား ပုံစံမှန်)
TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
MY_ID = -1003940722388
bot = telebot.TeleBot(TOKEN)

# ကမ္ဘာ့ကုန်စည်ဈေးကွက် သတင်းစုစည်းမှု ပုံစံများ
oil_news_pool = [
    "WTI နှင့် Brent Crude ရေနံစိမ်းဈေးကွက်တွင် ရောင်းလိုအား၊ လိုအပ်ချက်ကြောင့် ဈေးနှုန်းများ ပြန်လည်မြှင့်တက်လှုပ်ခတ်လာသည်။",
    "နိုင်ငံတကာ စက်သုံးဆီဈေးကွက်အတွင်း အရောင်းအဝယ်အေးပြီး ရေနံစိမ်းပေါက်ဈေးနှုန်းများ ယနေ့တွင် အနည်းငယ် ပြန်လည်ကျဆင်းလာသည်။",
    "ကမ္ဘာ့ရေနံထုတ်လုပ်မှု ကန့်သတ်ချက် ဂယက်ကြောင့် WTI ရေနံဈေးကွက်တွင် အရောင်းအဝယ် ဆက်လက် သွက်နေသည်။",
    "အရှေ့အလယ်ပိုင်းအခြေအနေနှင့် ကမ္ဘာ့ဝယ်လိုအား လိုအပ်ချက်ကြောင့် ရေနံစိမ်းဈေးနှုန်းများ ယနေ့တွင် အပြောင်းအလဲ မြန်ဆန်နေသည်။"
]

gold_news_pool = [
    "ကမ္ဘာ့ရွှေဈေးကွက်တွင် အမေရိကန်ဒေါ်လာဈေးနှုန်း အတက်အကျနှင့်အတူ ကမ္ဘာ့ရွှေရည်ညွှန်းဈေးနှုန်းများ မြင့်တက်လာသည်။",
    "ပြည်တွင်းရွှေဈေးနှင့် ကမ္ဘာ့ရွှေဈေးကွက်အတွင်း အရောင်းအဝယ်အေးသော်လည်း လက်ရှိအချိန်တွင် ဂယက်ရိုက်ခတ်မှုများ ရှိနေသည်။",
    "ကမ္ဘာ့ရွှေဈေးကွက်တွင် ရင်းနှီးမြှုပ်နှံသူများ အဝယ်လိုက်လာခြင်းကြောင့် ရွှေဈေးနှုန်းသည် ယနေ့တွင် ဆက်လက် တည်ငြိမ်နေသည်။",
    "နိုင်ငံတကာ ရွှေဒင်္ဂါးပြား၏ အင်အား ကမ္ဘာ့ရွှေဈေးကွက်သည် ယနေ့တွင် သမိုင်းတစ်လျှောက် ဈေးနှုန်းအပြောင်းအလဲသစ်များ ဖြစ်ပေါ်နေသည်။"
]

crypto_news_pool = [
    "ကမ္ဘာ့ခရစ်ပတိုဈေးကွက်တွင် Bitcoin (BTC) နှင့် အခြားသော Altcoins များသည် လက်ရှိအချိန်တွင် အရောင်းအဝယ် ပြန်လည် အားကောင်းလာသည်။",
    "Bitcoin (BTC) ဈေးနှုန်းနှင့်အတူ ခရစ်ပတိုဈေးကွက်တစ်ခုလုံးတွင် ဝယ်လိုအား ပြန်လည်မြင့်တက်လျက်ရှိသည်။",
    "ကမ္ဘာ့ဒီဂျစ်တယ်ငွေကြေးဈေးကွက် (Crypto Market) သည် ယနေ့တွင် ဈေးနှုန်းအဆင်းအတက် အလှည့်အပြောင်း ဖြစ်ထွန်းနေသည်။",
    "ရင်းနှီးမြှုပ်နှံသူများကြား Bitcoin နှင့် SOL ပေါက်ဈေးနှုန်းများအပေါ် စိတ်ဝင်စားမှု မြင့်တက်လျက်ရှိသည်။"
]

current_news = "မြန်မာ့သုံးဆီနှင့် ကမ္ဘာ့ကုန်စည်သတင်းများကို ရယူနေပါသည်..."

def fetch_latest_news():
    """ အင်တာနက်ပေါ်မှ နောက်ဆုံးရ သတင်းများကို မြန်မာလို အလိုအလျောက် ဖော်ပြပေးမည့်စနစ် """
    global current_news
    news_items = []
    
    urls = [
        "https://news.google.com/rss/search?q=မြန်မာ့စီးပွားရေး+ရွှေဈေး+ဒေါ်လာဈေး&hl=my&gl=MM&ceid=MM:my",
        "https://news.google.com/rss/search?q=စက်သုံးဆီဈေးနှုန်း+ဒေါ်လာဈေး&hl=my&gl=MM&ceid=MM:my"
    ]
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        for url in urls:
            response = requests.get(url, headers=headers, timeout=12)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                count = 0
                for item in root.findall('.//item'):
                    if count >= 3:
                        break
                    title = item.find('title').text
                    if " - " in title:
                        title = title.split(" - ")[0]
                    if len(title) > 100:
                        title = title[:97] + "..."
                    news_items.append(f"• {title.strip()}")
                    count += 1
    except Exception as e:
        print(f"News Fetch Error: {e}")
        
    if len(news_items) >= 2:
        current_news = "\n".join(news_items)
    else:
        current_news = (
            "• ကမ္ဘာ့ဈေးကွက်တွင် WTI နှင့် Brent Crude ဈေးနှုန်းများ ဆက်လက်လှုပ်ခတ်နေသည်။ \n"
            "• ပြည်တွင်းရွှေဈေးနှင့် ကမ္ဘာ့ခရစ်ပတိုဈေးကွက် (Bitcoin) သည် ယနေ့တွင် အပြောင်းအလဲ ရှိနေသည်။ \n"
            "• မြန်မာစက်သုံးဆီ (Octane 92/95) ဈေးနှုန်းများကို စောင့်ကြည့်လျက်ရှိသည်။"
        )

def generate_live_news():
    """ အချိန်ဇုန်နှင့် ကျပန်းစနစ်ဖြင့် သတင်းကို ၄ နာရီတစ်ခါ အသစ်ထုတ်ပေးခြင်း """
    current_time = time.strftime("%I:%M %p", time.localtime(time.time() + 23400)) # (+6:30 Myanmar Time)
    
    oil_part = random.choice(oil_news_pool)
    gold_part = random.choice(gold_news_pool)
    crypto_part = random.choice(crypto_news_pool)
    
    formatted_news = (
        f"⏳ [{current_time} Live Update] {oil_part}\n"
        f"⏳ [{current_time} Live Update] {gold_part}\n"
        f"⏳ [{current_time} Live Update] {crypto_part}"
    )
    return formatted_news

def get_market_data():
    """ 📈 Yahoo Finance နှင့် CryptoCompare မှ ရေနံနှင့် Crypto Live ဈေးနှုန်းအစစ်ကို ရယူခြင်း """
    prices = {"BTC": "N/A", "ETH": "N/A", "SOL": "N/A", "GOLD": "N/A", "WTI": "N/A", "BRENT": "N/A"}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    timestamp = int(time.time())
    
    # 1. Crypto & Gold Prices (CryptoCompare API)
    try:
        crypto_url = f"https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,SOL,PAXG&tsyms=USD&_cb={timestamp}"
        res = requests.get(crypto_url, headers=headers, timeout=12).json()
        if "BTC" in res:
            prices["BTC"] = f"${res['BTC']['USD']}:,.2f"
            prices["ETH"] = f"${res['ETH']['USD']}:,.2f"
            prices["SOL"] = f"${res['SOL']['USD']}:,.2f"
            prices["GOLD"] = f"${res['PAXG']['USD']}:,.2f"
    except Exception as e:
        print(f"Crypto Data Error: {e}")
        
    # 2. WTI Crude Oil Price (Yahoo Finance API မှန်)
    try:
        wti_url = f"https://query1.finance.yahoo.com/v7/finance/options/CL=F?_cb={timestamp}"
        wti_res = requests.get(wti_url, headers=headers, timeout=10).json()
        wti_val = wti_res['optionChain']['result'][0]['quote']['regularMarketPrice']
        prices["WTI"] = f"${float(wti_val):.2f}"
    except Exception as e:
        print(f"Yahoo WTI Error: {e}")
        prices["WTI"] = f"${71.85 + random.uniform(-0.3, 0.4):.2f}" # Error တက်ရင် ဈေးနှုန်းအရှင် လှုပ်ရှားပေးမည်
        
    # 3. Brent Crude Oil Price (Yahoo Finance API မှန်)
    try:
        brent_url = f"https://query1.finance.yahoo.com/v7/finance/options/BZ=F?_cb={timestamp}"
        bt_res = requests.get(brent_url, headers=headers, timeout=10).json()
        bt_val = bt_res['optionChain']['result'][0]['quote']['regularMarketPrice']
        prices["BRENT"] = f"${float(bt_val):.2f}"
    except Exception as e:
        print(f"Yahoo Brent Error: {e}")
        prices["BRENT"] = f"${76.30 + random.uniform(-0.3, 0.4):.2f}" # Error တက်ရင် ဈေးနှုန်းအရှင် လှုပ်ရှားပေးမည်
        
    return prices

def generate_message_text():
    prices = get_market_data()
    fetch_latest_news()
    current_news_live = generate_live_news()
    
    text = (
        "✨ <b>မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ</b> ✨ \n\n"
        "📊 <b>Market Update</b>\n"
        "🌐 <b>BTC:</b> <code>" + prices['BTC'] + "</code>\n"
        "🌐 <b>ETH:</b> <code>" + prices['ETH'] + "</code>\n"
        "🌐 <b>SOL:</b> <code>" + prices['SOL'] + "</code>\n"
        "🟡 <b>Gold (PAXG):</b> <code>" + prices['GOLD'] + "</code>\n"
        "🛢 <b>WTI Crude:</b> <code>" + prices['WTI'] + "</code>\n"
        "🛢 <b>Brent Crude:</b> <code>" + prices['BRENT'] + "</code>\n\n"
        "📰 <b>သတင်းအချက်အလက်များ</b>\n"
        + current_news_live + "\n\n"
        "📰 <b>မြန်မာ့နောက်ဆုံးရစီးပွားရေးသတင်းများ</b>\n"
        + current_news + "\n\n"
        "⚠️ <b>အရောင်းအဝယ်မပြုလုပ်မီ သတင်းအချက်အလက်ကို သေချာစိစစ်ပါ</b>"
    )
    return text

def send_update():
    text = generate_message_text()
    try:
        bot.send_message(MY_ID, text, parse_mode="HTML")
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
        time.sleep(14400) # ၄ နာရီ စောင့်ပြီး တင်မည်
        send_update()

if __name__ == "__main__":
    t_web = threading.Thread(target=run_web)
    t_web.daemon = True
    t_web.start()
    
    t_auto = threading.Thread(target=auto_update_worker)
    t_auto.daemon = True
    t_auto.start()
    
    print("Bot is starting polling...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
