import telebot
import os
import requests
import time
import threading
from flask import Flask

# 1. Flask Server Setup
app = Flask('')

@app.route('/')
def home():
    return "Bot is live!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. Setup Bot
TOKEN = os.getenv('BOT_TOKEN')
MY_ID = os.getenv('MY_ID')
bot = telebot.TeleBot(TOKEN)

# 3. စျေးနှုန်းဆွဲယူသည့် Function (Binance API ကို ရိုးရိုးရှင်းရှင်း ပြန်ပြင်ထားသည်)
def get_market_prices():
    try:
        # BTC Price
        btc_res = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT', timeout=10).json()
        # ETH Price
        eth_res = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT', timeout=10).json()
        
        btc = float(btc_res['price'])
        eth = float(eth_res['price'])

        return {
            "BTC": f"${btc:,.2f}",
            "ETH": f"${eth:,.2f}"
        }
    except Exception as e:
        print(f"API Error: {e}")
        return None

# 4. Auto Send Loop
def auto_send_loop():
    print(f"Auto Loop Started for ID: {MY_ID}")
    time.sleep(10)
    while True:
        try:
            if MY_ID:
                prices = get_market_prices()
                if prices:
                    msg = (f"📊 <b>Market Update</b>\n\n"
                           f"₿ <b>BTC:</b> <code>{prices['BTC']}</code>\n"
                           f"Ξ <b>ETH:</b> <code>{prices['ETH']}</code>")
                    bot.send_message(int(MY_ID), msg, parse_mode='HTML')
                    print("✅ Update Sent!")
            time.sleep(3600) # ၁ နာရီတစ်ခါ ပို့မည်
        except Exception as e:
            print(f"Loop Error: {e}")
            time.sleep(60)

# 5. Commands
@bot.message_handler(commands=['price'])
def send_price(message):
    prices = get_market_prices()
    if prices:
        msg = f"📊 <b>Current Prices</b>\n\nBTC: {prices['BTC']}\nETH: {prices['ETH']}"
        bot.reply_to(message, msg, parse_mode='HTML')
    else:
        bot.reply_to(message, "⚠️ API Error: စျေးနှုန်းဆွဲမရဖြစ်နေပါသည်။")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, f"Bot အလုပ်လုပ်နေပါပြီ! သင့်ရဲ့ ID က {message.chat.id} ဖြစ်ပါတယ်။")

# 6. Run Bot
if __name__ == "__main__":
    # Threading သုံးပြီး အလုပ်ခွဲလုပ်ခိုင်းခြင်း
    threading.Thread(target=run_web).start()
    threading.Thread(target=auto_send_loop).start()
    
    print("Bot is starting...")
    bot.infinity_polling()
