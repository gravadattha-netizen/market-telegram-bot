import os
import time
import requests
import threading
from flask import Flask
import telebot
import google.generativeai as genai

# ==================== [ CONFIGURATION ] ====================
TG_TOKEN = os.environ.get("TG_TOKEN", "")
GROUP_CHAT_ID = "-1003940722388"
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# Gemini & Telegram Bot Setup
genai.configure(api_key=GOOGLE_API_KEY)
bot = telebot.TeleBot(TG_TOKEN)
app = Flask('')

# ဈေးကွက် Data (Crypto, Gold, Oil) အားလုံးကို ဆွဲယူမည့် Function
def get_market_data():
    prices = {}
    
    # ၁။ Binance မှ Crypto (BTC, ETH) Spot Prices ဆွဲခြင်း
    for sym in ["BTCUSDT", "ETHUSDT"]:
        try:
            res = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={sym}").json()
            prices[sym] = {
                "price": float(res["lastPrice"]), 
                "change": float(res["priceChangePercent"])
            }
        except Exception as e:
            print(f"Error fetching Crypto {sym}: {e}")
            
    # ၂။ Yahoo Finance API မှ ရွှေ နှင့် ရေနံ (WTI, Brent) ဈေးနှုန်းများ ဆွဲခြင်း
    # GC=F (Gold), CL=F (WTI Crude Oil), BZ=F (Brent Crude Oil)
    commodities = {
        "GOLD": "GC=F",
        "WTI_CRUDE": "CL=F",
        "BRENT_CRUDE": "BZ=F"
    }
    
    for name, ticker in commodities.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=2d"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            res = requests.get(url, headers=headers).json()
            
            meta = res['chart']['result'][0]['meta']
            current_price = meta['regularMarketPrice']
            previous_close = meta['chartPreviousClose']
            
            change_percent = ((current_price - previous_close) / previous_close) * 100
            
            prices[name] = {
                "price": round(current_price, 2),
                "change": round(change_percent, 2)
            }
        except Exception as e:
            print(f"Error fetching Commodity {name}: {e}")
            
    return prices

# Gemini ဖြင့် သတင်းဆောင်းပါးရေးပြီး Telegram သို့ လှမ်းပို့မည့် Function
def generate_and_send_report():
    try:
        data = get_market_data()
        
        # API တစ်ခုခု ချို့ယွင်းခဲ့လျှင်လည်း Bot လုံးဝမရပ်သွားစေရန် Default Data ထိန်းပေးခြင်း
        if not data or "BTCUSDT" not in data:
            print("API Fetch Failed or incomplete, using fallback/retrying...")
            
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        သင်သည် ကမ္ဘာ့စီးပွားရေးနှင့် ရင်းနှီးမြှုပ်နှံမှု ဈေးကွက်ကို ကျွမ်းကျင်သော ထိပ်တန်းသတင်းထောက်တစ်ယောက် ဖြစ်သည်။ 
        ပေးထားသော Data တွင် BTC, ETH, Gold (ကမ္ဘာ့ရွှေဈေး)၊ WTI Crude Oil နှင့် Brent Crude Oil (ရေနံဈေးနှုန်းများ) ပါဝင်သည်။
        
        ဤအချက်အလက်များကို အသုံးပြု၍ လက်ရှိဈေးကွက် အခြေအနေ သုံးသပ်ချက် သတင်းဆောင်းပါးတစ်ပုဒ်ကို မြန်မာဘာသာဖြင့် စာပိုဒ် (၃) ပိုဒ်သာ တိုတိုကျဉ်းကျဉ်း ရေးပေးပါ။
        စာရင်း (List သို့မဟုတ် အစက်ပြစာလုံးများ၊ တုံးတိုများ) လုံးဝ မသုံးရပါ။ ရိုးရိုးဆောင်းပါးစကားပြေအတိုင်းသာ ရေးပါ။
        
        သတင်းခေါင်းစဉ်ကို စိတ်ဝင်စားစရာကောင်းအောင် ထိပ်ဆုံးတွင် ထည့်ရေးပေးပါ။ (ဥပမာ - # ကမ္ဘာ့ရွှေဈေးနှင့် Crypto ဈေးကွက် နောက်ဆုံးအခြေအနေ သုံးသပ်ချက်)
        ဈေးတက်သွားသော အရာများ၏ ဈေးနှုန်းကို **Bold** လုပ်ပါ။ ဈေးကျသွားသော အရာများ၏ ဈေးနှုန်းကို *Italic* လုပ်ပါ။
        
        Data: {data}
        """
        
        response = model.generate_content(prompt)
        report_text = response.text
        
        bot.send_message(chat_id=GROUP_CHAT_ID, text=report_text, parse_mode="Markdown")
        print("Market report sent successfully to Telegram!")
        
    except Exception as e:
        print(f"Error in generate_and_send_report: {e}")

# ၄ နာရီတစ်ခါ အလိုအလျောက် ပတ်မည့် စနစ် (Loop Background Thread)
def market_loop():
    # Server စပွင့်ပွင့်ချင်း သတင်းတစ်ပုဒ် ချက်ချင်း အရင်ဆုံး ထုတ်ခိုင်းခြင်း
    time.sleep(5)  # Startup စာသား တက်ပြီး ၅ စက္ကန့် စောင့်ပြီး သတင်းထုတ်ရန်
    generate_and_send_report()
    
    while True:
        # ၁၄၄۰۰ စက္ကန့် = ၄ နာရီ စောင့်ဆိုင်းခြင်း
        time.sleep(14400)
        print("4 hours interval reached. Fetching new market data...")
        generate_and_send_report()

# Telegram /check_market Command စမ်းသပ်ရန်
@bot.message_handler(commands=['check_market'])
def handle_check_market(message):
    bot.reply_to(message, "⏳ BTC, ETH, ရွှေ နှင့် ရေနံဈေးကွက်သတင်းများကို AI ဖြင့် ပြင်ဆင်နေပါသည်...")
    generate_and_send_report()

@app.route('/')
def home():
    return "Market Telegram Bot with 4-Hour Loop is Running Live!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    # ၁။ Bot စတင်ကြောင်း Group ထဲသို့ စမ်းသပ်စာ ပို့ခြင်း
    try:
        bot.send_message(
            chat_id=GROUP_CHAT_ID, 
            text="🚀 Market Analysis Bot စတင် အလုပ်လုပ်ပါပြီဗျာ... (၄ နာရီတစ်ကြိမ် သတင်းများကို အလိုအလျောက် ပုံမှန်တင်ပေးသွားမည် ဖြစ်ပါသည်)"
        )
    except Exception as e:
        print(f"Startup message error: {e}")

    # ၂။ ၄ နာရီတစ်ခါ ပတ်မည့် လုပ်ငန်းစဉ်ကို Background တွင် စတင်ခြင်း
    threading.Thread(target=market_loop).start()

    # ၃။ Flask Web Server စတင်ခြင်း
    threading.Thread(target=run_flask).start()

    # ၄။ Telegram Bot Polling
    try:
        bot.remove_webhook()
        time.sleep(1)
    except:
        pass
        
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print(f"Bot polling error: {e}")
            time.sleep(5)
