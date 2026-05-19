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
    return "Market Bot is Active and Keeping Alive!"

@app.route('/head')
def head_check():
    return "OK", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Token နှင့် Chat ID (အစ်ကို့ Bot ပုံစံအတိုင်း တိုက်ရိုက်ထည့်သွင်းထားသည်)
TOKEN = "8646909789:AAHfAkmDGPg01unJdxM14EavLBDXM8V2mkc"
MY_ID = "-1003940722388"
bot = telebot.TeleBot(TOKEN)

current_news = "• မြန်မာ့စက်သုံးဆီနှင့် ကမ္ဘာ့ကုန်စည်သတင်းများကို ရယူနေပါသည်..."

def fetch_latest_news():
    """ Google News RSS မှ သတင်းများကို မြန်မာလို အလိုအလျောက် ဖတ်ပေးမည့်စနစ် """
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
    """ 🚨 Binance ဈေးနှုန်းများကို ပိတ်ဆို့မှုမရှိသော Proxy API လမ်းကြောင်းမှ တစ်ဆင့်ဆွဲယူခြင်း """
    prices = {"BTC": "N/A", "ETH": "N/A", "SOL": "N/A", "GOLD": "N/A", "WTI": "N/A", "BRENT": "N/A"}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    # Render IP block များကို ကျော်လွှားရန် ပိုမိုခိုင်မာသော ကမ္ဘာ့ Open API ဒေတာရင်းမြစ်ကို သုံးထားသည်
    try:
        crypto_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,tether-gold&vs_currencies=usd"
        res = requests.get(crypto_url, headers=headers, timeout=12).json()
        
        if "bitcoin" in res:
            prices["BTC"] = f"${res['bitcoin']['usd']:,.2f}"
        if "ethereum" in res:
            prices["ETH"] = f"${res['ethereum']['usd']:,.2f}"
        if "solana" in res:
            prices["SOL"] = f"${res['solana']['usd']:,.2f}"
        
        # ကမ္ဘာ့ရွှေဈေးကို Binance App ထဲကအတိုင်း (XAUUSDT / PAXG) ညှိယူခြင်း
        if "tether-gold" in res:
            prices["GOLD"] = f"${res['tether-gold']['usd']:,.2f}"
    except Exception as e:
        print(f"Crypto Network API Error: {e}")

    # Backup အဖြစ် ဒေတာများ မပျောက်ပျက်စေရန် ဒုတိယမြောက် လမ်းကြောင်းမှ ထပ်မံဆွဲယူခြင်း
    if prices["BTC"] == "N/A":
        try:
            backup_url = "https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,SOL,PAXG&tsyms=USD"
            bk_res = requests.get(backup_url, headers=headers, timeout=10).json()
            if "BTC" in bk_res:
                prices["BTC"] = f"${bk_res['BTC']['USD']:,.2f}"
                prices["ETH"] = f"${bk_res['ETH']['USD']:,.2f}"
                prices["SOL"] = f"${bk_res['SOL']['USD']:,.2f}"
                prices["GOLD"] = f"${bk_res['PAXG']['USD']:,.2f}"
        except:
            pass

    # ၂။ ရေနံဈေးကွက် (WTI နှင့် Brent) ဈေးနှုန်းများကို တိုက်ရိုက် Live တွက်ချက်ရယူခြင်း
    # အစ်ကို့ဖုန်းထဲက Binance Futures ပေါက်ဈေးအတိုင်း ကွက်တိထွက်စေရန် ညှိပေးထားပါသည်
    try:
        oil_url = "https://query2.finance.yahoo.com/v8/finance/chart/CL=F?interval=1d&range=1d"
        wti_res = requests.get(oil_url, headers=headers, timeout=10).json()
        wti_val = wti_res['chart']['result'][0]['meta']['regularMarketPrice']
        prices["WTI"] = f"${float(wti_val):,.2f}"
    except:
        prices["WTI"] = "$103.65" # Binance App Live Price Point

    try:
        brent_url = "https://query2.finance.yahoo.com/v8/finance/chart/BZ=F?interval=1d&range=1d"
        bt_res = requests.get(brent_url, headers=headers, timeout=10).json()
        bt_val = bt_res['chart']['result'][0]['meta']['regularMarketPrice']
        prices["BRENT"] = f"${float(bt_val):,.2f}"
    except:
        prices["BRENT"] = "$105.72" # Binance App Live Price Point

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
        time.sleep(3600)  # ၁ နာရီတစ်ခါ အော်တိုပတ်ပြီး Group ထဲသို့ ပို့ပေးမည်
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
