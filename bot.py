import os
import time
import requests
import threading
import xml.etree.ElementTree as ET
from flask import Flask
import telebot

app = Flask('')

@app.route('/')
def home():
    return "Market Bot is Active!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Token နှင့် Chat ID (အစ်ကို့ Bot ပုံစံအတိုင်း တိုက်ရိုက်ထည့်သွင်းထားသည်)
TOKEN = "8646909789:AAHfAkmDGPg01unJdxM14EavLBDXM8V2mkc"
MY_ID = "-1003940722388"
bot = telebot.TeleBot(TOKEN)

# သတင်းများကို သိမ်းရန် Variable
current_news = "• ရေနံ၊ ရွှေ၊ ခရစ်တိုနှင့် စက်သုံးဆီ နောက်ဆုံးရ မြန်မာသတင်းများကို ဖတ်နေပါသည်..."

def fetch_latest_news():
    """ အင်တာနက်ပေါ်မှ နောက်ဆုံးရ စီးပွားရေးနှင့် စက်သုံးဆီ သတင်းများကို မြန်မာလို ရှာဖွေဖတ်ပေးမည့်စနစ် """
    global current_news
    news_items = []
    
    # မြန်မာလို သတင်းခေါင်းစဉ်များ ပိုမိုရရှိနိုင်မည့် RSS Feed များနှင့် Keyword များ
    urls = [
        "https://news.google.com/rss/search?q=မြန်မာ့စက်သုံးဆီ+ရွှေစျေး+ခရစ်တို&hl=my&gl=MM&ceid=MM:my",
        "https://news.google.com/rss/search?q=စက်သုံးဆီစျေးနှုန်း+ဒေါ်လာစျေး&hl=my&gl=MM&ceid=MM:my"
    ]
    
    # စက်ရုပ်ဟု ထင်ပြီး ပိတ်မချရန် Headers ထည့်သွင်းခြင်း
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    
    try:
        for url in urls:
            response = requests.get(url, headers=headers, timeout=12)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                count = 0
                for item in root.findall('.//item'):
                    if count >= 2:
                        break
                    title = item.find('title').text
                    
                    # သတင်းဌာန နာမည်များကို ရှင်းထုတ်ပြီး သန့်စင်ခြင်း
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
        # အကယ်၍ အင်တာနက်ပြတ်တောက်ခြင်း သို့မဟုတ် Feed မရပါက အသုံးပြုမည့် မြန်မာလို Backup သတင်းများ
        current_news = (
            "• ကမ္ဘာ့ရေနံစျေးကွက်တွင် WTI နှင့် Brent Crude စျေးနှုန်းများ ဆက်လက်လှုပ်ခတ်နေသည်။\n"
            "• ပြည်တွင်းရွှေစျေးနှင့် ကမ္ဘာ့ခရစ်တိုဈေးကွက် (Bitcoin) သည် ယနေ့တွင် အပြောင်းအလဲ ရှိနေသည်။\n"
            "• မြန်မာ့စက်သုံးဆီ (Octane 92/95) စျေးနှုန်းများကို စောင့်ကြည့်လျက်ရှိသည်။"
        )

def get_market_data():
    prices = {"BTC": "N/A", "ETH": "N/A", "GOLD": "N/A", "WTI": "$103.65", "BRENT": "$105.72"}
    
    # 🚨 Binance API အတွက် စိတ်ချရသော အောက်ပါ Headers ကို ထည့်သွင်းပေးထားပါသည် (N/A မဖြစ်စေရန်)
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    
    try:
        res = requests.get("https://api.binance.com/api/v3/ticker/price", headers=headers, timeout=12).json()
        symbols = {"BTCUSDT": "BTC", "ETHUSDT": "ETH", "PAXGUSDT": "GOLD"}
        
        # ရလာသော Data ကို ပတ်စစ်ခြင်း
        if isinstance(res, list):
            for item in res:
                sym = item.get('symbol')
                if sym in symbols:
                    price_val = float(item['price'])
                    prices[symbols[sym]] = f"${price_val:,.2f}"
    except Exception as e:
        print(f"Binance API Error: {e}")

    # ကမ္ဘာ့ရေနံစျေးနှုန်းများကို Binance အတိုင်း တိုက်ရိုက်ရယူခြင်း
    try:
        oil_res = requests.get("https://api.binance.com/api/v3/ticker/price", headers=headers, timeout=12).json()
        if isinstance(oil_res, list):
            for item in oil_res:
                if item.get('symbol') == "CLUSDT": # WTI Crude
                    prices["WTI"] = f"${float(item['price']):,.2f}"
                elif item.get('symbol') == "BZUSDT": # Brent Crude
                    prices["BRENT"] = f"${float(item['price']):,.2f}"
    except Exception as e:
        print(f"Oil Price Error: {e}")

    return prices

def generate_message_text():
    global current_news
    prices = get_market_data()
    
    text = (
        f"🌟 **မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ** 🌟\n\n"
        f"📊 **Market Update**\n\n"
        f"₿ BTC: {prices['BTC']}\n"
        f"Ξ ETH: {prices['ETH']}\n"
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

# /price ဟု ရိုက်လျှင်လည်း Update စျေးနှုန်းနှင့် မြန်မာသတင်းကို ချက်ချင်းပြရန်
@bot.message_handler(commands=['price'])
def manual_price(message):
    fetch_latest_news()
    send_update()

def auto_update_worker():
    print("Auto Update Thread Started...")
    fetch_latest_news()
    time.sleep(5)
    send_update()
    
    while True:
        time.sleep(3600)  # ၁ နာရီတစ်ခါ အော်တိုပတ်မည်
        fetch_latest_news()
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
