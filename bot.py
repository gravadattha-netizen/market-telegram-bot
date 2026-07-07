import os
import time
import requests
import threading
from flask import Flask, render_template_string
import telebot
import google.generativeai as genai

# ==================== [ CONFIGURATION ] ====================
# Render ရဲ့ Environment Variable ထံမှ Token ကို အလိုအလျောက် လှမ်းယူခြင်း
TG_TOKEN = os.environ.get("TG_TOKEN", "")
GROUP_CHAT_ID = "-1003940722388"

# API Key ကို Render Environment ထံမှ ဖတ်ယူမည်
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# Gemini Setup
genai.configure(api_key=GOOGLE_API_KEY)
bot = telebot.TeleBot(TG_TOKEN)
app = Flask('')

# Binance မှ Data ဆွဲမည့် Function
def get_market_data():
    prices = {}
    # Spot Prices (BTC, ETH) ကို သေချာပေါက် ဆွဲယူခြင်း
    for sym in ["BTCUSDT", "ETHUSDT"]:
        try:
            res = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={sym}").json()
            prices[sym] = {
                "price": float(res["lastPrice"]), 
                "change": float(res["priceChangePercent"])
            }
        except Exception as e:
            print(f"Error fetching {sym}: {e}")
            pass
    return prices

# Gemini ဖြင့် ဗမာလို သတင်းရေးပြီး Telegram ပို့မည့် Function
def send_market_report():
    try:
        data = get_market_data()
        
        # အကယ်၍ အင်တာနက်ကြောင့် Data လုံးဝမကျလာလျှင်လည်း Bot လမ်းခုလတ်မှာ ရပ်မသွားစေရန် ထိန်းခြင်း
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
        
        # Telegram သို့ ပို့ခြင်း
        bot.send_message(chat_id=GROUP_CHAT_ID, text=report_text, parse_mode="Markdown")
        print("Market report sent successfully to Telegram!")
        
    except Exception as e:
        print(f"Error in send_market_report: {e}")

# Command ဖြင့် စမ်းသပ်ရန် (/check_market ဟု Bot ထံတိုက်ရိုက်ပို့လျှင် တန်းလုပ်မည်)
@bot.message_handler(commands=['check_market'])
def handle_check_market(message):
    bot.reply_to(message, "⏳ ဈေးကွက်သတင်းကို AI ဖြင့် မြန်မြန် ပြန်ဆင်ပေးပါမည်...")
    send_market_report()

@app.route('/')
def home():
    return "Market Telegram Bot is Running Live!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    # ၁။ Server စပွင့်တာနဲ့ Group ထဲကို စမ်းသပ်စာ ချက်ချင်း လှမ်းပို့ခိုင်းခြင်း
    try:
        print("Sending initial startup message...")
        bot.send_message(
            chat_id=GROUP_CHAT_ID, 
            text="🚀 Market Analysis Bot စတင် အလုပ်လုပ်ပါပြီဗျာ... ခေတ္တစောင့်ဆိုင်းပေးပါ။ Gemini မှ အချက်အလက်များ လှမ်းယူနေပါသည်။"
        )
    except Exception as e:
        print(f"Startup message error: {e}")

    # ၂။ သတင်းတစ်ပုဒ် အလိုအလျောက် ထုတ်ပေးမည့် Thread စတင်ခြင်း
    threading.Thread(target=send_market_report).start()

    # ၃။ Flask Web Server ပတ်ခြင်း
    threading.Thread(target=run_flask).start()

    # ၄။ Telegram Bot Polling (Webhook ဖြုတ်ပြီး အသစ်ပြန်စခြင်း)
    def run_bot():
        try:
            bot.remove_webhook()
            time.sleep(1)
        except:
            pass
        
        while True:
            try:
                bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)
            except Exception as e:
                print(f"Bot polling error: {e}")
                time.sleep(5)

    run_bot()
