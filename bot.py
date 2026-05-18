import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

import telebot
import google.generativeai as genai
import os
import requests
import threading
import time

# ၁။ Key များကို Render မှ ဆွဲယူခြင်း
BOT_TOKEN = os.getenv('BOT_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_KEY')
MY_ID = os.getenv('MY_ID') # Group ID ထည့်ထားလျှင်

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

# ၂။ Binance မှ ဈေးနှုန်းဆွဲယူခြင်း
def get_market_prices():
    try:
        res = requests.get('https://api.binance.com/api/v3/ticker/price', params={'symbols': '["BTCUSDT","ETHUSDT"]'}, timeout=15).json()
        prices = {item['symbol']: float(item['price']) for item in res}
        return {
            "BTC": f"${prices.get('BTCUSDT', 0):,.2f}",
            "ETH": f"${prices.get('ETHUSDT', 0):,.2f}"
        }
    except: return None

# ၃။ /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါ! Market Analysis Bot နိုးနေပါပြီ။")

# ၄။ AI နှင့် စကားပြောခြင်း
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "ခေတ္တ စောင့်ဆိုင်းပေးပါ။")

# ၅။ Bot ကို စတင်ပတ်ခြင်း
if __name__ == "__main__":
    bot.infinity_polling()
    if __name__ == "__main__":
    # Web Server အသေးစားလေးကို အရင် နှိုးလိုက်တာပါ
    keep_alive() 
    
    # ပြီးမှ သင့် Bot ရဲ့ အလုပ်လုပ်မယ့် Function ကို ဒီအောက်မှာ ဆက် run ပါ
    # ဥပမာ - သင်က while True loop သုံးထားရင် အဲ့ဒီ function ကို လှမ်းခေါ်ပေးပါ
    
    print("Bot is starting...")
    # bot.infinity_polling()  <-- သင့် Bot ရဲ့ မူလ run တဲ့ command ကို ဒီနားမှာ ထားပါ
