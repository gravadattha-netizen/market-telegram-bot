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

# Binance မှ Crypto Prices (BTC, ETH) သီးသန့် ဆွဲယူမည့် Function
def get_market_data():
    prices = {}
    for sym in ["BTCUSDT", "ETHUSDT"]:
        try:
            res = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={sym}").json()
            prices[sym] = {
                "price": float(res["lastPrice"]), 
                "change": float(res["priceChangePercent"])
            }
        except Exception as e:
            print(f"Error fetching {sym}: {e}")
    return prices

# Gemini ဖြင့် သတင်းဆောင်းပါးရေးပြီး Telegram သို့ တန်းပို့မည့် Function
def send_market_report():
    try:
        data = get_market_data()
        
        # အကယ်၍ API ဆွဲရတာ အခက်အခဲရှိခဲ့လျှင်လည်း Bot လုံးဝမရပ်သွားစေရန် ထိန်းခြင်း
        if not data:
            data = {
                "BTCUSDT": {"price": 0.0, "change": 0.0},
                "ETHUSDT": {"price": 0.0, "change": 0.0}
            }
            
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        သင်သည် ကျွမ်းကျင်သော စီးပွားရေးသတင်းထောက်တစ်ယောက် ဖြစ်သည်။ သင့်အလုပ်မှာ ပေးထားသော Data ကို သတင်းဆောင်းပါးအဖြစ် ပြောင်းလဲပေးရန် ဖြစ်သည်။
        စာရင်း (List) များ လုံးဝမသုံးရ။ ပေးထားသော အခြေအနေများကို တိုကျဉ်းစွာ ပြောပါ။
        အောက်ပါ data ကိုအသုံးပြု၍ စီးပွားရေးသတင်းဆောင်းပါးတစ်ပုဒ်ကို မြန်မာဘာသာဖြင့် ရေးပါ။ အပိုဒ် (၃) ပိုဒ်သာ ရေးပါ။
        သတင်း ခေါင်းစဉ် ကို ချီးကျူးဇူး အခြေအနေအတိုင်း ရေးသားပေးပါ။ (ဥပမာ - # ဈေးကွက်အတွင်း အကျိုးသက်ရောက်စေသည့် ရင်းနှီးမြှုပ်နှံမှုများ)
        
        ဈေးတက်သွားသော ပစ္စည်းများ၏ ဈေးနှုန်းကို **Bold** လုပ်ပါ။ ဈေးကျသွားသော ပစ္စည်း၏ ဈေးနှုန်းကို *Italic* လုပ်ပါ။
        Data: {data}
        """
        
        response = model.generate_content(prompt)
        report_text = response.text
        
        # Telegram သို့ သတင်းလှမ်းပို့ခြင်း
        bot.send_message(chat_id=GROUP_CHAT_ID, text=report_text, parse_mode="Markdown")
        print("Market report sent successfully!")
        
    except Exception as e:
        print(f"Error in send_market_report: {e}")

# Telegram /check_market Command စမ်းသပ်ရန်
@bot.message_handler(commands=['check_market'])
def handle_check_market(message):
    bot.reply_to(message, "⏳ ဈေးကွက်သတင်းကို AI ဖြင့် ပြန်ဆင်ပေးပါမည်...")
    send_market_report()

@app.route('/')
def home():
    return "Market Telegram Bot is Running Live!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    # ၁။ Bot စတင်ကြောင်း Group ထဲသို့ ချက်ချင်း အသိပေးခြင်း
    try:
        bot.send_message(
            chat_id=GROUP_CHAT_ID, 
            text="🚀 Market Analysis Bot စတင် အလုပ်လုပ်ပါပြီဗျာ... ခေတ္တစောင့်ဆိုင်းပေးပါ။ Gemini မှ အချက်အလက်များ လှမ်းယူနေပါသည်။"
        )
    except Exception as e:
        print(f"Startup message error: {e}")

    # ၂။ သတင်းထုတ်ပေးမည့် လုပ်ငန်းစဉ်ကို Thread ဖြင့် ချက်ချင်း စတင်ခြင်း
    threading.Thread(target=send_market_report).start()

    # ၃။ Flask Web Server စတင်ခြင်း
    threading.Thread(target=run_flask).start()

    # ၄။ Telegram Bot Polling (Webhook ဖြုတ်ပြီး အသစ်ပြန်စခြင်း)
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
