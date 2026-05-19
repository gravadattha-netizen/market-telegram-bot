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
current_news = "• ရေနံ၊ ရွှေ၊ ခရစ်တိုနှင့် စက်သုံးဆီ နောက်ဆုံးရသတင်းများကို အလိုအလျောက် ဖတ်နေပါသည်..."

def fetch_latest_news():
    """ အစ်ကိုဘာမှနှိပ်စရာမလိုဘဲ အင်တာနက်ပေါ်က နောက်ဆုံးရသတင်းများကို Auto သွားဖတ်ပေးမည့်စနစ် """
    global current_news
    news_items = []
    
    # Google News RSS Feeds (မြန်မာ့စီးပွားရေးနှင့် ကမ္ဘာ့ကုန်စည်စျေးကွက် သတင်းများ)
    urls = [
        "https://news.google.com/rss/search?q=Myanmar+fuel+oil+gold+market&hl=en-US&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=crypto+crude+oil+price+update&hl=en-US&gl=US&ceid=US:en"
    ]
    
    try:
        for url in urls:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                # Feed တစ်ခုစီမှ ထိပ်ဆုံးသတင်း ၂ ပုဒ်စီကို နှုတ်ယူခြင်း
                count = 0
                for item in root.findall('.//item'):
                    if count >= 2:
                        break
                    title = item.find('title').text
                    # စာသားအရမ်းရှည်ပါက သပ်ရပ်အောင် ဖြတ်တောက်ရန်
                    if len(title) > 90:
                        title = title[:87] + "..."
                    news_items.append(f"• {title}")
                    count += 1
    except Exception as e:
        print(f"News Fetch Error: {e}")
        
    if news_items:
        current_news = "\n".join(news_items)
    else:
        # အကယ်၍ အင်တာနက်ပြတ်တောက်ပြီး ဆွဲမရပါက ပြပေးမည့် Backup သတင်းအချက်အလက်
        current_news = (
            "• ကမ္ဘာ့ရေနံစျေးကွက်တွင် WTI နှင့် Brent Crude စျေးနှုန်းများ ဆက်လက်လှုပ်ခတ်နေသည်။\n"
            "• ရွှေစျေးနှင့် Crypto ဈေးကွက် (Bitcoin) သည် ယနေ့တွင် အရောင်းအဝယ် အားကောင်းလျက်ရှိသည်။\n"
            "• မြန်မာ့စက်သုံးဆီ (Octane 92/95) စျေးနှုန်းများမှာ ကမ္ဘာ့စျေးအပြောင်းအလဲအပေါ် မူတည်၍ တည်ငြိမ်နေသည်။"
        )

def get_market_data():
    prices = {"BTC": "N/A", "ETH": "N/A", "GOLD": "N/A", "WTI": "$103.65", "BRENT": "$105.72"}
    
    # Binance API မှ Crypto နှင့် ရွှေစျေးကို တိုက်ရိုက်ဆွဲယူခြင်း
    try:
        res = requests.get("https://api.binance.com/api/v3/ticker/price", timeout=10).json()
        symbols = {"BTCUSDT": "BTC", "ETHUSDT": "ETH", "PAXGUSDT": "GOLD"}
        for item in res:
            sym = item.get('symbol')
            if sym in symbols:
                price_val = float(item['price'])
                prices[symbols[sym]] = f"${price_val:,.2f}"
    except Exception as e:
        print(f"Binance API Error: {e}")

    return prices

def generate_message_text():
    global current_news
    prices = get_market_data()
    
    # အစ်ကို ပြင်ခိုင်းထားသည့် "သတင်းအချက်အလက်များ" ခေါင်းစဉ်အတိုင်း ပြင်ဆင်ထားပါသည်
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

# /price ဟု လက်လှမ်းရိုက်လျှင်လည်း လက်ရှိ Update စျေးနှင့် သတင်းကို ချက်ချင်း ဆွဲပြပေးရန်
@bot.message_handler(commands=['price'])
def manual_price(message):
    fetch_latest_news() # လက်ရှိ သတင်းကို ချက်ချင်းသွားဖတ်ခိုင်းခြင်း
    send_update()

def auto_update_worker():
    print("Auto Update Thread Started...")
    # စက်စနိုးချင်းမှာ သတင်းအသစ်ကိုပါ တစ်ခါတည်း အလိုအလျောက် သွားဖတ်ခိုင်းခြင်း
    fetch_latest_news()
    time.sleep(5)
    send_update()
    
    while True:
        # ၁ နာရီ (၃၆၀၀ စက္ကန့်) စောင့်မည်
        time.sleep(3600)
        # ၁ နာရီပြည့်တိုင်း အစ်ကိုဘာမှနှိပ်စရာမလိုဘဲ သတင်းများကို နောက်ဆုံးရ အပ်ဒိတ် အလိုအလျောက် သွားဖတ်မည်
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
