import telebot
import os
import requests
import time
import threading
from flask import Flask

# ၁။ Render Live ဖြစ်စေဖို့ Flask ဆောက်ခြင်း
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    # Render က ပေးတဲ့ PORT (သို့မဟုတ်) 10000 ကို သုံးပါမယ်
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ၂။ Environment Variables ဆွဲယူခြင်း
BOT_TOKEN = os.getenv('BOT_TOKEN')
MY_ID = os.getenv('MY_ID')

bot = telebot.TeleBot(BOT_TOKEN)

# ၃။ Binance ကနေ စျေးနှုန်းဆွဲယူတဲ့ Function
def get_market_prices():
    try:
        url = 'https://api.binance.com/api/v3/ticker/price'
        params = {'symbols': '["BTCUSDT","ETHUSDT"]'}
        res = requests.get(url, params=params, timeout=10).json()
        prices = {item['symbol']: float(item['price']) for item in res}
        return {
            "BTC": f"${prices.get('BTCUSDT', 0):,.2f}",
            "ETH": f"${prices.get('ETHUSDT', 0):,.2f}"
        }
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return None

# ၄။ စျေးနှုန်းကို ၁ နာရီတစ်ခါ ပို့ပေးမည့် Loop
def auto_send_loop():
    while True:
        prices = get_market_prices()
        if prices and MY_ID:
            msg = (f"📊 <b>Market Update</b>\n\n"
                   f"₿ <b>BTC:</b> {prices['BTC']}\n"
                   f"Ξ <b>ETH:</b> {prices['ETH']}")
            try:
                bot.send_message(MY_ID, msg, parse_mode='HTML')
            except:
                pass
        time.sleep(3600)

@bot.message_handler(commands=['price'])
def send_price(message):
    prices = get_market_prices()
    if prices:
        msg = f"📊 <b>Current Prices</b>\nBTC: {prices['BTC']}\nETH: {prices['ETH']}"
        bot.reply_to(message, msg, parse_mode='HTML')
    else:
        bot.reply_to(message, "စျေးနှုန်းဆွဲယူရတာ အဆင်မပြေဖြစ်နေပါတယ်။")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot အလုပ်လုပ်နေပါပြီခင်ဗျာ။ /price နဲ့ စျေးနှုန်းကြည့်နိုင်ပါတယ်။")

if __name__ == "__main__":
    # Web Server ကို Thread တစ်ခုနဲ့ အရင် Run ပါမယ် (ဒါမှ Render က Live ပေးမှာပါ)
    threading.Thread(target=run_web).start()
    # Auto Send ကိုလည်း Thread တစ်ခုနဲ့ Run ပါမယ်
    threading.Thread(target=auto_send_loop, daemon=True).start()
    
    print("Bot is starting...")
    bot.infinity_polling()
