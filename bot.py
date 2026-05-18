import telebot
import os
import requests
import time
import threading
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Bot is running perfectly!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# API Keys
BOT_TOKEN = os.getenv('BOT_TOKEN')
MY_ID = os.getenv('MY_ID')

bot = telebot.TeleBot(BOT_TOKEN)

def get_market_prices():
    try:
        # Binance API ကို တစ်ခုချင်းစီ ခေါ်ကြည့်ပါမယ်
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
    while True:
        # Bot စတက်တက်ချင်း စာပို့အောင် ခဏစောင့်ပါမယ်
        time.sleep(10) 
        prices = get_market_prices()
        if prices and MY_ID:
            msg = f"📊 <b>Market Update</b>\n\n₿ BTC: <code>{prices['BTC']}</code>\nΞ ETH: <code>{prices['ETH']}</code>"
            try:
                bot.send_message(MY_ID, msg, parse_mode='HTML')
                print("Message sent successfully!")
            except Exception as e:
                print(f"Send Error: {e}")
        
        # ၁ နာရီ (၃၆၀၀ စက္ကန့်) စောင့်ပါမယ်
        time.sleep(3600)

@bot.message_handler(commands=['price'])
def send_price(message):
    prices = get_market_prices()
    if prices:
        msg = f"📊 <b>Current Prices</b>\nBTC: {prices['BTC']}\nETH: {prices['ETH']}"
        bot.reply_to(message, msg, parse_mode='HTML')
    else:
        bot.reply_to(message, "စျေးနှုန်းယူလို့မရသေးပါဘူး။ ခဏနေမှ ပြန်စမ်းကြည့်ပါ။")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot အလုပ်လုပ်နေပါပြီ! /price လို့ ရိုက်ကြည့်ပါ။")

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    threading.Thread(target=auto_send_loop, daemon=True).start()
    print("Bot is starting...")
    bot.infinity_polling()
