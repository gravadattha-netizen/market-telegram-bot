import telebot
import os
import requests
import time
import threading
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and fetching prices!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# API Keys
BOT_TOKEN = os.getenv('BOT_TOKEN')
# MY_ID ကို Integer (ကိန်းဂဏန်း) အဖြစ်ပြောင်းရန် အရေးကြီးသည်
try:
    MY_ID = int(os.getenv('MY_ID'))
except:
    MY_ID = None

bot = telebot.TeleBot(BOT_TOKEN)

def get_market_prices():
    try:
        btc_res = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT', timeout=10).json()
        eth_res = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT', timeout=10).json()
        
        btc_price = float(btc_res['price'])
        eth_price = float(eth_res['price'])
        
        return {
            "BTC": f"${btc_price:,.2f}",
            "ETH": f"${eth_price:,.2f}"
        }
    except Exception as e:
        print(f"API Error: {e}")
        return None

def auto_send_loop():
    # Bot စတက်ပြီး ၁၀ စက္ကန့်အကြာတွင် ပထမဆုံးအကြိမ် စျေးနှုန်းစပို့မည်
    time.sleep(10)
    while True:
        prices = get_market_prices()
        if prices and MY_ID:
            msg = (f"📊 <b>Market Update</b>\n\n"
                   f"₿ <b>BTC:</b> <code>{prices['BTC']}</code>\n"
                   f"Ξ <b>ETH:</b> <code>{prices['ETH']}</code>")
            try:
                bot.send_message(MY_ID, msg, parse_mode='HTML')
                print("Market Update sent!")
            except Exception as e:
                print(f"Telegram Send Error: {e}")
        
        # ၁ နာရီ (၃၆၀၀ စက္ကန့်) တစ်ခါ ပို့ရန်
        time.sleep(3600)

@bot.message_handler(commands=['price'])
def send_price(message):
    prices = get_market_prices()
    if prices:
        msg = f"📊 <b>Current Prices</b>\nBTC: {prices['BTC']}\nETH: {prices['ETH']}"
        bot.reply_to(message, msg, parse_mode='HTML')

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot အလုပ်လုပ်နေပါပြီခင်ဗျာ။ /price လို့ ရိုက်ကြည့်နိုင်ပါတယ်။")

if __name__ == "__main__":
    # Flask Server ကို အရင် Run ပါ (Render Live ဖြစ်နေစေရန်)
    threading.Thread(target=run_web).start()
    
    # စျေးနှုန်းပို့မည့် Loop ကို Thread တစ်ခုဖြင့် Run ပါ
    threading.Thread(target=auto_send_loop, daemon=True).start()
    
    print("Bot is starting...")
    bot.infinity_polling()
