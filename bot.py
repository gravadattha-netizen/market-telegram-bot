import time
import requests
import threading
import os
from flask import Flask, render_template_string
import telebot
import google.generativeai as genai

# ==================== [ CONFIGURATION ] ====================
# Render ရဲ့ Environment Variable ထဲကနေ Token ကို ဘေးကင်းစွာ လှမ်းဖတ်ခြင်း
TG_TOKEN = os.environ.get("TG_TOKEN", "")
GROUP_CHAT_ID = "-1003940722388"
# API Key ကို Render Environment ထဲက ဖတ်မည်
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
# Gemini Setup
genai.configure(api_key=GOOGLE_API_KEY)
bot = telebot.TeleBot(TG_TOKEN)
app = Flask('')

# Binance မှ Data ဆွဲယူမည့် Function
def get_market_data():
    prices = {}
    # Spot Prices (BTC, ETH)
    for sym in ["BTCUSDT", "ETHUSDT"]:
        try:
            res = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={sym}").json()
            prices[sym] = {"price": float(res["lastPrice"]), "change": float(res["priceChangePercent"])}
        except: pass
    # Futures Prices (Crude Oil, Gold, Brent)
    for sym in ["CLUSDT", "XAUUSDT", "BZUSDT"]:
        try:
            res = requests.get(f"https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={sym}").json()
            prices[sym] = {"price": float(res["lastPrice"]), "change": float(res["priceChangePercent"])}
        except: pass
    return prices

# Gemini ဖြင့် မြန်မာလို သတင်းရေးပြီး Telegram ပို့မည့် Function
def send_market_report():
    try:
        data = get_market_data()
        if not data:
            print("No market data fetched.")
            return
            
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        သင်သည် ကျွမ်းကျင်သော စီးပွားရေးသတင်းထောက်တစ်ယောက် ဖြစ်သည်။ သင့်အလုပ်မှာ ပေးထားသော Data ကို သတင်းဆောင်းပါးအဖြစ် ပြောင်းလဲပေးရန် ဖြစ်သည်။
        စာရင်း (List) များ လုံးဝမသုံးရ။ ပေးထားသော အခေါ်အဝေါ်များကိုသာ တိကျစွာ သုံးပါ။
        အောက်ပါ data ကိုအသုံးပြု၍ စီးပွားရေးသတင်းဆောင်းပါးတစ်ပုဒ်ကို မြန်မာဘာသာဖြင့် ရေးပါ။ အပိုဒ် (၃) ပိုဒ်သာ ရေးပါ။
        သတင်း ခေါင်းစဉ် ကို ဈေးကွက် အခြေအနေအတိုင်း ရေးသားပေးပါ။ (ဥပမာ- # ဈေးကွက်အတွင်း အကျဘက်ဦးတည်နေသည့် ရင်းနှီးမြှုပ်နှံမှုပစ္စည်းများ)
        
        ဈေးတက်သွားသော ပစ္စည်းများ၏ ဈေးနှုန်းကို **Bold** လုပ်ပါ။ ဈေးကျသွားသော ပစ္စည်းများ၏ ဈေးနှုန်းကို *Italic* လုပ်ပါ။
        Data: {data}
        """
        response = model.generate_content(prompt)
        report_text = response.text
        
        # Telegram သို့ ပို့ခြင်း
        bot.send_message(chat_id=GROUP_CHAT_ID, text=report_text, parse_mode="Markdown")
        print("Market report sent successfully to Telegram!")
    except Exception as e:
        print(f"Error in send_market_report: {e}")

# Command ဖြင့် စမ်းသပ်ရန် (/check_market ဟု Bot ထဲရိုက်လျှင် တန်းပတ်မည်)
@bot.message_handler(commands=['check_market'])
def handle_check_market(message):
    bot.reply_to(message, "⏳ ဈေးကွက်သတင်းကို AI ဖြင့် ပြင်ဆင်နေပါသည်...")
    send_market_report()

@app.route('/')
def home():
    return "Bot is Running Live!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def run_bot():
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    # ၁။ စဖွင့်ဖွင့်ချင်း သတင်းတစ်ပုဒ် အလိုအလျောက် တန်းပို့ခိုင်းခြင်း
    threading.Thread(target=send_market_report).start()
    
    # ၂။ Flask Web Server ကို Thread နဲ့ သီးသန့်ပတ်ခြင်း
    threading.Thread(target=run_flask).start()
    
    # ၃။ Telegram Bot Polling ကို အောက်ဆုံးမှာမှ တိုက်ရိုက်ပတ်ခြင်း (ဒီနေရာမှာပဲ ထားရပါမယ်)
def run_bot():
    # လက်ရှိ ငြိနေတဲ့ Webhook သို့မဟုတ် အဟောင်းတွေကို လုံးဝ အပြတ်ရှင်းချပစ်ခြင်း
    try:
        bot.remove_webhook()
        time.sleep(1)
    except:
        pass

    # Bot စပတ်ခြင်း
    while True:
        try:
            bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Bot polling error: {e}")
            time.sleep(5)
run_bot()
