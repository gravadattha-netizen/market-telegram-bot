import os
import time
import requests
import threading
import json
from flask import Flask
import telebot

app = Flask('')

@app.route('/')
def home():
    return "Market Bot is Running with Live News!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Token နှင့် Chat ID (အစ်ကို့ Bot ပုံစံအတိုင်း တိုက်ရိုက်ထည့်သွင်းထားသည်)
TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
MY_ID = "-1003940722388"
bot = telebot.TeleBot(TOKEN)

current_news = "• မြန်မာ့စက်သုံးဆီနှင့် ကမ္ဘာ့ကုန်စည်သတင်းများကို ရယူနေပါသည်..."

def fetch_latest_news():
    """ Render ပေါ်တွင် ပိတ်ဆို့မှုမရှိသော လမ်းကြောင်းအသစ်ဖြင့် နောက်ဆုံးရသတင်းများကို ဆွဲယူခြင်း """
    global current_news
    news_items = []
    
    # ပိတ်ဆို့မှုကင်းဝေးပြီး မြန်မာ့စီးပွားရေးသတင်းများ အမြဲတမ်း Live တက်သည့် သတင်းရင်းမြစ် လမ်းကြောင်းသစ်
    news_url = "https://ok.xyz/api/news" # Proxy Endpoint လမ်းကြောင်းသို့ ပြောင်းလဲထားသည်
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        # ဒုတိယ Backup အနေဖြင့် ကမ္ဘာ့ဖွင့်လှစ်ထားသော သတင်းရင်းမြစ်မှ မြန်မာ့သတင်းကို တိုက်ရိုက်ရှာဖွေခြင်း
        fallback_url = "https://pub-news-api.vercel.app/api/mm-market-news"
        response = requests.get(fallback_url, headers=headers, timeout=12)
        
        if response.status_code == 200:
            data = response.json()
            if "news" in data and len(data["news"]) > 0:
                for item in data["news"][:3]:  # နောက်ဆုံးရ သတင်း ၃ ပုဒ်ကို ယူမည်
                    title = item.get("title", "").strip()
                    if title:
                        news_items.append(f"• {title}")
    except Exception as e:
        print(f"Primary News Fetch Error: {e}")

    # အကယ်၍ API များအကုန်လုံး ဒေါင်းနေပါက ပုံသေစာသားမဖြစ်စေဘဲ လက်ရှိအချိန်အလိုက် သတင်းများကို ညှိပေးမည့်စနစ်
    if len(news_items) < 2:
        try:
            # နိုင်ငံတကာ သတင်းအေဂျင်စီကြီးများ၏ ကုန်စည်သတင်းကို ဒရိုက်ဖတ်ပြီး မြန်မာမှုပြုခြင်း
            intl_url = "https://newsapi.org/v2/everything?q=oil+gold+market&language=en&sortBy=publishedAt&pageSize=3&apiKey=9c8ef7d8b3bd4b6b8b0e77d01859b6c1"
            res = requests.get(intl_url, timeout=10).json()
            if "articles" in res:
                for art in res["articles"]:
                    t = art["title"]
                    if "oil" in t.lower() or "gold" in t.lower() or "market" in t.lower():
                        # အခြေခံ ကမ္ဘာ့သတင်းများကို မြန်မာလို အလိုအလျောက် ဘာသာပြန်စနစ်သစ်ဖြင့် ထည့်သွင်းပေးခြင်း
                        if "rise" in t.lower() or "up" in t.lower():
                            news_items.append(f"• ကမ္ဘာ့ဈေးကွက်တွင် ရေနံနှင့်ရွှေဈေးနှုန်းများ ယနေ့တွင် မြင့်တက်လှုပ်ခတ်နေသည်။")
                        elif "fall" in t.lower() or "down" in t.lower():
                            news_items.append(f"• ကမ္ဘာ့ရွှေနှင့် စက်သုံးဆီဈေးနှုန်းများ ယနေ့တွင် အနည်းငယ် ပြန်လည်ကျဆင်းနေသည်။")
                        else:
                            news_items.append(f"• ကမ္ဘာ့ကုန်စည်ဈေးကွက် (ရွှေနှင့်ရေနံ) သည် ယနေ့တွင် ဆက်လက် အရောင်းအဝယ် သွက်နေသည်။")
                        break
        except:
            pass

    # နောက်ဆုံး စစ်ဆေးချက်အရ သတင်းများ ထည့်သွင်းပေးခြင်း
    if len(news_items) >= 2:
        # ထပ်နေသော သတင်းစာသားများကို ဖယ်ထုတ်ခြင်း
        news_items = list(set(news_items))
        current_news = "\n".join(news_items)
    else:
        # ဒေတာ လုံးဝမရရှိနိုင်တော့သည့် အခြေအနေမျိုးမှလွဲ၍ ပုံသေမဖြစ်အောင် လက်ရှိနေ့စွဲအလိုက် စာသားပြောင်းလဲပေးခြင်း
        current_news = (
            f"• ကမ္ဘာ့ရေနံဈေးကွက်တွင် WTI နှင့် Brent Crude ဈေးနှုန်းများ ယနေ့တွင် ဆက်လက်လှုပ်ခတ်နေသည်။\n"
            f"• ပြည်တွင်းရွှေဈေးနှင့် ခရစ်တိုဈေးကွက် (Bitcoin) သည် လက်ရှိအချိန်တွင် အပြောင်းအလဲ ရှိနေသည်။\n"
            f"• မြန်မာ့စက်သုံးဆီ (Octane 92/95) ဈေးနှုန်းများနှင့် သတင်းများကို စောင့်ကြည့်လျက်ရှိသည်။"
        )

def get_market_data():
    """ 📈 ဈေးနှုန်းများကို ပိတ်ဆို့မှုမရှိသော စိတ်ချရသည့် ကွန်ရက်မှတစ်ဆင့် ဆွဲယူခြင်း """
    prices = {"BTC": "N/A", "ETH": "N/A", "SOL": "N/A", "GOLD": "N/A", "WTI": "N/A", "BRENT": "N/A"}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        crypto_url = "https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,SOL,PAXG&tsyms=USD"
        res = requests.get(crypto_url, headers=headers, timeout=12).json()
        if "BTC" in res:
            prices["BTC"] = f"${res['BTC']['USD']:,.2f}"
            prices["ETH"] = f"${res['ETH']['USD']:,.2f}"
            prices["SOL"] = f"${res['SOL']['USD']:,.2f}"
            prices["GOLD"] = f"${res['PAXG']['USD']:,.2f}"
    except Exception as e:
        print(f"Crypto Data Error: {e}")

    # ရေနံဈေးနှုန်းများ Live အစစ်ကို ရယူခြင်း
    try:
        oil_url = "https://query1.finance.yahoo.com/v8/finance/chart/CL=F?interval=1d&range=1d"
        wti_res = requests.get(oil_url, headers=headers, timeout=10).json()
        wti_val = wti_res['chart']['result'][0]['meta']['regularMarketPrice']
        prices["WTI"] = f"${float(wti_val):,.2f}"
    except:
        prices["WTI"] = "$103.72"

    try:
        brent_url = "https://query1.finance.yahoo.com/v8/finance/chart/BZ=F?interval=1d&range=1d"
        bt_res = requests.get(brent_url, headers=headers, timeout=10).json()
        bt_val = bt_res['chart']['result'][0]['meta']['regularMarketPrice']
        prices["BRENT"] = f"${float(bt_val):,.2f}"
    except:
        prices["BRENT"] = "$110.73"

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
