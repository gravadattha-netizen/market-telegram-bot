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

# Token နှင့် Chat ID
TOKEN = "8646909789:AAHfAkmDGPg01unJdxM14EavLBDXM8V2mkc"
MY_ID = "-1003940722388"
bot = telebot.TeleBot(TOKEN)

current_news = "• မြန်မာ့စက်သုံးဆီနှင့် ကမ္ဘာ့ကုန်စည်သတင်းများကို ရယူနေပါသည်..."

def fetch_latest_news():
    """ အင်တာနက်ပေါ်မှ နောက်ဆုံးရ သတင်းများကို မြန်မာလို အလိုအလျောက် ဖတ်ပေးမည့်စနစ် """
    global current_news
    news_items = []
    
    urls = [
        "https://news.google.com/rss/search?q=မြန်မာ့စက်သုံးဆီ+ရွှေစျေး+ခရစ်တို&hl=my&gl=MM&ceid=MM:my",
        "https://news.google.com/rss/search?q=စက်သုံးဆီစျေးနှုန်း+ဒေါ်လာစျေး&hl=my&gl=MM&ceid=MM:my"
    ]
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
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
            "• ကမ္ဘာ့ရေနံစျေးကွက်တွင် WTI နှင့် Brent Crude စျေးနှုန်းများ ဆက်လက်လှုပ်ခတ်နေသည်။\n"
            "• ပြည်တွင်းရွှေစျေးနှင့် ကမ္ဘာ့ခရစ်တိုဈေးကွက် (Bitcoin) သည် ယနေ့တွင် အပြောင်းအလဲ ရှိနေသည်။\n"
            "• မြန်မာ့စက်သုံးဆီ (Octane 92/95) စျေးနှုန်းများကို စောင့်ကြည့်လျက်ရှိသည်။"
        )

def get_market_data():
    """ 🚨 Binance Futures (fapi) API စစ်စစ်ထံမှ Live စျေးနှုန်းများ ဆွဲယူခြင်း """
    prices = {"BTC": "N/A", "ETH": "N/A", "SOL": "N/A", "GOLD": "N/A", "WTI": "N/A", "BRENT": "N/A"}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    # ၁။ Binance Futures API ထံမှ စျေးနှုန်းအားလုံးကို တစ်ခါတည်း ဆွဲယူခြင်း
    try:
        # Binance Futures API endpoint ကို အသုံးပြုပါ
        binance_url = "https://fapi.binance.com/fapi/v1/ticker/price"
        res = requests.get(binance_url, headers=headers, timeout=15).json()
        
        if isinstance(res, list):
            for item in res:
                sym = item.get('symbol')
                price_val = float(item.get('price', 0))
                
                if sym == "BTCUSDT":
                    prices["BTC"] = f"${price_val:,.2f}"
                elif sym == "ETHUSDT":
                    prices["ETH"] = f"${price_val:,.2f}"
                elif sym == "SOLUSDT":
                    prices["SOL"] = f"${price_val:,.2f}"
                elif sym == "PAXGUSDT":
                    prices["GOLD"] = f"${price_val:,.2f}"
                elif sym == "CLUSDT":    # WTI Crude Oil
                    prices["WTI"] = f"${price_val:,.2f}"
                elif sym == "BZUSDT":    # Brent Crude Oil
                    prices["BRENT"] = f"${price_val:,.2f}"
    except Exception as e:
        print(f"Binance Futures API Error: {e}")

    # ၂။ အကယ်၍ Futures ဘက်မှာ PAXG (ရွှေ) မရှိပါက Spot API ဘက်ကနေ Backup ပြန်ဆွဲပေးမည့်စနစ်
    if prices["GOLD"] == "N/A":
        try:
            spot_url = "https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT"
            spot_res = requests.get(spot_url, headers=headers, timeout=10).json()
            if "price" in spot_res:
                prices["GOLD"] = f"${float(spot_res['price']):,.2f}"
        except:
            # ၎င်းနေရာတွင် စျေးနှုန်းပုံသေမသုံးပါနှင့်
            print("PAXG Gold Price error.")

    return prices

def generate_message_text():
    global current_news
    prices = get_market_data()
    
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
