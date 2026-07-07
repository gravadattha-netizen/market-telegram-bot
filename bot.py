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

# Setup
genai.configure(api_key=GOOGLE_API_KEY)
bot = telebot.TeleBot(TG_TOKEN)
app = Flask('')

# ၁။ Binance & Yahoo Finance မှ ဈေးနှုန်းများ အမှားအယွင်းမရှိ ဆွဲယူခြင်း
def get_market_data():
    prices = {}
    
    # Crypto (BTC, ETH)
    for sym in ["BTCUSDT", "ETHUSDT"]:
        try:
            res = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={sym}", timeout=10).json()
            if "lastPrice" in res:
                prices[sym] = {
                    "price": float(res["lastPrice"]), 
                    "change": float(res["priceChangePercent"])
                }
        except Exception as e:
            print(f"Error Crypto {sym}: {e}")
            
    # Commodities (Gold, WTI, Brent) - Yahoo Finance Request with strict headers
    commodities = {
        "GOLD": "GC=F",
        "WTI_CRUDE": "CL=F",
        "BRENT_CRUDE": "BZ=F"
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for name, ticker in commodities.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=2d"
            res = requests.get(url, headers=headers, timeout=10).json()
            
            meta = res['chart']['result'][0]['meta']
            current_price = meta['regularMarketPrice']
            previous_close = meta['chartPreviousClose']
            change_percent = ((current_price - previous_close) / previous_close) * 100
            
            prices[name] = {
                "price": round(current_price, 2),
                "change": round(change_percent, 2)
            }
        except Exception as e:
            print(f"Error Commodity {name}: {e}")
            
    return prices

# ၂။ Gemini သတင်းထုတ်ပြန်ပြီး Telegram သို့ လှမ်းပို့ခြင်း
def generate_and_send_report():
    try:
        print("Fetching data for Gemini report...")
        data = get_market_data()
        
        # အကယ်၍ Data ဆွဲရခက်ခဲခဲ့လျှင် Backup ပုံစံဖြင့် ဆက်သွားရန်
        if not data:
            print("Failed to fetch market data.")
            return

        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        သင်သည် ကမ္ဘာ့စီးပွားရေးနှင့် ရင်းနှီးမြှုပ်နှံမှု ဈေးကွက်ကို ကျွမ်းကျင်သော ထိပ်တန်းသတင်းထောက်တစ်ယောက် ဖြစ်သည်။ 
        ပေးထားသော Data တွင် BTC, ETH, Gold (ကမ္ဘာ့ရွှေဈေး)၊ WTI Crude Oil နှင့် Brent Crude Oil (ရေနံဈေးနှုန်းများ) ပါဝင်သည်။
        
        ဤအချက်အလက်များကို အသုံးပြု၍ လက်ရှိဈေးကွက် အခြေအနေ သုံးသပ်ချက် သတင်းဆောင်းပါးတစ်ပုဒ်ကို မြန်မာဘာသာဖြင့် စာပိုဒ် (၃) ပိုဒ်သာ တိုတိုကျဉ်းကျဉ်း ရေးပေးပါ။
        စာရင်း (List သို့မဟုတ် အစက်ပြစာလုံးများ၊ တုံးတိုများ) လုံးဝ မသုံးရပါ။ ရိုးရိုးဆောင်းပါးစကားပြေအတိုင်းသာ ဇာတ်တိုက် ရေးပါ။
        
        သတင်းခေါင်းစဉ်ကို စိတ်ဝင်စားစရာကောင်းအောင် ထိပ်ဆုံးတွင် ထည့်ရေးပေးပါ။ (ဥပမာ - # ကမ္ဘာ့ရွှေဈေးနှင့် Crypto ဈေးကွက် နောက်ဆုံးအခြေအနေ သုံးသပ်ချက်)
        ဈေးတက်သွားသော အရာများ၏ ဈေးနှုန်းကို **Bold** လုပ်ပါ။ ဈေးကျသွားသော အရာများ၏ ဈေးနှုန်းကို *Italic* လုပ်ပါ။
        
        Data: {data}
        """
        
        response = model.generate_content(prompt)
        report_text = response.text
        
        # Markdown parsing error မတက်အောင် လုံခြုံစိတ်ချရသော ပုံစံဖြင့် ပို့ခြင်း
        try:
            bot.send_message(chat_id=GROUP_CHAT_ID, text=report_text, parse_mode="Markdown")
        except Exception:
            bot.send_message(chat_id=GROUP_CHAT_ID, text=report_text) # Fallback if Markdown fails
            
        print("Report successfully sent!")
        
    except Exception as e:
        print(f"Error in generate_and_send_report: {e}")

# ၃။ နောက်ကွယ်မှ ၄ နာရီတစ်ခါ ပတ်မည့် Loop
def market_loop():
    # Server တက်ပြီး ၁၅ စက္ကန့်အကြာတွင် Conflict ငြိမ်သွားမှ ပထမဆုံးအစီရင်ခံစာကို စတင်ထုတ်ခိုင်းခြင်း
    time.sleep(15)
    generate_and_send_report()
    
    while True:
        time.sleep(14400) # ၄ နာရီ ခြားခြင်း
        generate_and_send_report()

# Command လက်ခံခြင်း
@bot.message_handler(commands=['check_market'])
def handle_check_market(message):
    bot.reply_to(message, "⏳ BTC, ETH, ရွှေ နှင့် ရေနံဈေးကွက်သတင်းများကို AI ဖြင့် ပြင်ဆင်နေပါသည်...")
    generate_and_send_report()

@app.route('/')
def home():
    return "Market Bot is Running Perfectly!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Main Execution
if __name__ == "__main__":
    # Flask ကို Background Thread ဖြင့် အရင်မောင်းခြင်း
    threading.Thread(target=run_flask, daemon=True).start()

    # Automatic Loop ကို သီးသန့် Thread ဖြင့် ခွဲမောင်းခြင်း
    threading.Thread(target=market_loop, daemon=True).start()

    # Bot Polling စတင်ခြင်း (Conflict ၄၀၉ ပြဿနာကို အလိုအလျောက် ရှင်းထုတ်ရန် စနစ်)
    print("Starting Bot Polling...")
    while True:
        try:
            # နေရာဟောင်းက Session တွေကို အရင်ဖျက်ထုတ်ပစ်ခြင်း
            bot.delete_webhook(drop_pending_updates=True)
            time.sleep(1)
            bot.polling(none_stop=True, timeout=30, long_polling_timeout=20)
        except Exception as e:
            print(f"Polling error encountered, restarting session in 5s...: {e}")
            time.sleep(5)
