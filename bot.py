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

# API Keys (Render Environment ထဲက ယူထားတာပါ)
BOT_TOKEN = os.getenv('BOT_TOKEN')
RAW_ID = os.getenv('MY_ID')

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
    # Bot စတက်တက်ချင်း စျေးနှုန်းကို ချက်ချင်း တစ်ခါအရင်ပို့မည်
    time.sleep(5)
    print(f"Attempting to send update to ID: {RAW_ID}")
    
    while True:
        prices = get_market_prices()
        if prices and RAW_ID:
            msg = (f"📊 <b>Market Update</b>\n\n"
                   f"₿ <b>BTC:</b> <code>{prices['BTC']}</code>\n"
                   f"Ξ <b>ETH:</b> <code>{prices['ETH']}</code>")
            try:
                # RAW_ID ကို string ကနေ integer ပြောင်းပြီး ပို့ပေးပါမယ်
                bot.send_message(int(RAW_ID), msg, parse_mode='HTML')
                print("Market Update sent successfully!")
            except Exception as e:
                print(f"Telegram Send Error: {e}")
        
        # ၁ နာရီ (၃၆၀၀ စက္ကန့်) စောင့်မည်
        time.sleep(3600)

@bot.message_handler(commands=['price'])
def send_price(message):
    prices = get_market_prices()
    if prices:
        msg = f"📊 <b>Current Prices</b>\nBTC: {prices['BTC']}\nETH: {prices['ETH']}"
        bot.reply_to(message, msg, parse_mode='HTML')

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot အလုပ်လုပ်နေပါပြီ! /price လို့ ရိုက်ကြည့်ပါ။")

if __name__ == "__main__":
    # Web Server Run
    threading.Thread(target=run_web).start()
    
    # Auto Send Loop Run
    threading.Thread(target=auto_send_loop, daemon=True).start()
    
    print("Bot is starting up...")
    bot.infinity_polling()
