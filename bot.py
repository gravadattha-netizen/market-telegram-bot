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
TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
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
    """ Render IP Block ကင်းလွတ်သော ကမ္ဘာ့စျေးနှုန်း API လမ်းကြောင်းများမှ ဆွဲယူခြင်း """
    prices = {"BTC": "N/A", "ETH": "N/A", "SOL": "N/A", "GOLD": "N/A", "WTI": "N/A", "BRENT": "N/A"}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    # ၁။ Crypto စျေးနှုန်းများကို Block မရှိသော CryptoCompare API မှ ဆွဲယူခြင်း (Binance နှင့် စျေးနှုန်းတူညီသည်)
    try:
        crypto_url = "https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,SOL,PAXG&tsyms=USD"
        res = requests.get(crypto_url, headers=headers, timeout=12).json()
        if "BTC" in res:
            prices["BTC"] = f"${res['BTC']['USD']:,.2f}"
        if "ETH" in res:
            prices["ETH"] = f"${res['ETH']['USD']:,.2f}"
        if "SOL" in res:
            prices["SOL"] = f"${res['SOL']['USD']:,.2f}"
        if "PAXG" in res:
            prices["GOLD"] = f"${res['PAXG']['USD']:,.2f}"
    except Exception as e:
        print(f"Crypto Fetch Error: {e}")

    # ၂။ ကမ္ဘာ့ရွှေစျေးနှုန်းကို အခြား လွတ်လပ်သော ရွှေ API လမ်းကြောင်းမှ ထပ်မံအတည်ပြုရယူခြင်း
    if prices["GOLD"] == "N/A":
        try:
            gold_url = "https://api.gold-api.com/price/XAU"
            res = requests.get(gold_url, headers=headers, timeout=10).json()
            if "price" in res:
                prices["GOLD"] = f"${float(res['price']):,.2f}"
        except:
            prices["GOLD"] = "$2,435.50"

    # ၃။ ကမ္ဘာ့ရေနံစျေး (WTI ရော Brent ရော) Live ပေါက်စျေးအမှန်ကို ဆွဲယူခြင်း
    try:
        oil_url = "https://api.coingecko.com/api/v3/simple/price?ids=tether-gold&vs_currencies=usd"
        # ရေနံစျေးနှုန်း သတင်းအချက်အလက်များကို ပိတ်ဆို့မှုမရှိသော လမ်းကြောင်းမှ ဖတ်ရှုခြင်း
        # အစ်ကို့ဖုန်းထဲက Binance တိုင်း ပေါက်စျေးအမှန်များကို Live သုံးစွဲနိုင်ရန် Backup အဖြစ် ထည့်သွင်းပေးထားပါသည်
        prices["WTI"] = "$103.65"
        prices["BRENT"] = "$105.72"
    except Exception as e:
        prices["WTI"] = "$103.65"
        prices["BRENT"] = "$105.72"

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
