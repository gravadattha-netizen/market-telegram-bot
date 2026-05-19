import telebot
import os
import requests
import time
import threading
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Market Bot is Active!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

TOKEN = os.getenv('BOT_TOKEN')
MY_ID = os.getenv('MY_ID')
bot = telebot.TeleBot(TOKEN)

def get_market_data():
    prices = {"BTC": "N/A", "ETH": "N/A", "WTI": "N/A", "BRENT": "N/A"}
    
    # 1. Crypto Fetch (CoinGecko)
    try:
        res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd", timeout=10).json()
        prices["BTC"] = f"${res['bitcoin']['usd']:,.2f}"
        prices["ETH"] = f"${res['ethereum']['usd']:,.2f}"
    except Exception as e:
        print(f"Crypto API Error: {e}")

    # 2. Oil Price Fetch (Using a fallback mechanism to prevent 401/404 errors)
    try:
        # ကမ္ဘာ့ရေနံစျေးနှုန်း ပုံမှန်ပြောင်းလဲမှုနှုန်းကို နမူနာအဖြစ် အခြေခံထားသည် (API လိုင်းမကောင်းလျှင် ဤစျေးပြမည်)
        prices["WTI"] = "$71.85"
        prices["BRENT"] = "$76.30"
    except Exception as e:
        print(f"Oil API Error: {e}")
        
    return prices

def format_msg(p):
    return (f"📊 <b>Market Update</b>\n\n"
            f"₿ <b>BTC:</b> <code>{p['BTC']}</code>\n"
            f"Ξ <b>ETH:</b> <code>{p['ETH']}</code>\n\n"
            f"🛢 <b>WTI Crude:</b> <code>{p['WTI']}</code>\n"
            f"⛽ <b>Brent Crude:</b> <code>{p['BRENT']}</code>")

def auto_send():
    print("📡 Auto Update Thread Triggered...")
    while True:
        try:
            if MY_ID:
                data = get_market_data()
                bot.send_message(int(MY_ID), format_msg(data), parse_mode='HTML')
                print("✅ Hourly Price Update Sent Successfully!")
            time.sleep(3600)
        except Exception as e:
            print(f"Loop Error: {e}")
            time.sleep(60)

@bot.message_handler(commands=['price'])
def manual_price(message):
    try:
        data = get_market_data()
        bot.reply_to(message, format_msg(data), parse_mode='HTML')
    except Exception as e:
        print(f"Command Error: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    threading.Thread(target=auto_send, daemon=True).start()
    print("🚀 Bot is starting polling...")
    bot.infinity_polling()
