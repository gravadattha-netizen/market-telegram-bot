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
                    if count >= 3:  # သတင်း ၃ ပုဒ်အထိ တိုးမြှင့်ဖတ်ရှုမည်
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
    """ 📈 Yahoo Finance နှင့် CryptoCompare မှ ရေနံနှင့် Crypto Live ဈေးနှုန်းအစစ်ကို ရယူခြင်း """
    prices = {"BTC": "N/A", "ETH": "N/A", "SOL": "N/A", "GOLD": "N/A", "WTI": "N/A", "BRENT": "N/A"}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
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
        
    # 2. WTI Crude Oil Price (Yahoo Finance Live API မှန်)
    try:
        wti_url = f"https://query1.finance.yahoo.com/v7/finance/options/CL=F?_cb={timestamp}"
        wti_res = requests.get(wti_url, headers=headers, timeout=10).json()
        wti_val = wti_res['optionChain']['result'][0]['quote']['regularMarketPrice']
        prices["WTI"] = f"${float(wti_val):.2f}"
    except Exception as e:
        print(f"Yahoo WTI Error: {e}")
        prices["WTI"] = "$71.85" # Fallback အဖြစ် အဟောင်းအတိုင်း ခဏထိန်းထားမည်
        
    # 3. Brent Crude Oil Price (Yahoo Finance Live API မှန်)
    try:
        brent_url = f"https://query1.finance.yahoo.com/v7/finance/options/BZ=F?_cb={timestamp}"
        bt_res = requests.get(brent_url, headers=headers, timeout=10).json()
        bt_val = bt_res['optionChain']['result'][0]['quote']['regularMarketPrice']
        prices["BRENT"] = f"${float(bt_val):.2f}"
    except Exception as e:
        print(f"Yahoo Brent Error: {e}")
        prices["BRENT"] = "$76.30" # Fallback အဖြစ် အဟောင်းအတိုင်း ခဏထိန်းထားမည်
        
    return prices
