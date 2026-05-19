import telebot
import os
import requests
import time
import threading
from flask import Flask

# 1. Flask Web Server Setup (Render အတွက်)
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and fetching prices!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. Environment Variables ယူခြင်း
BOT_TOKEN = os.getenv('BOT_TOKEN')
RAW_ID = os.getenv('MY_ID')

bot = telebot.TeleBot(BOT_TOKEN)

# 3. Market Price ဆွဲသည့် Function
def get_market_prices():
    try:
        # Binance API သုံးပြီး BTC နှင့် ETH ယူခြင်း
        btc_res = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT', timeout=15).json()
        eth_res = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT', timeout=15).json()
        
        btc_price = float(btc_res['price'])
        eth_price = float(eth_res['price'])
        
        return {
            "BTC": f"${btc_price:,.2f}",
            "ETH": f"${eth_price:,.2f}"
        }
    except Exception as e:
        print(f"❌ API Error: {e}")
        return None

# 4. စျေးနှုန်း အလိုအလျောက် ပို့ပေးမည့် Loop
def auto_send_loop():
    print(f"📡 Auto Send Loop Started. Target ID: {RAW_ID}")
    
    # ပထမဆုံး စက္ကန့် ၃၀ စောင့်မည် (Server တက်လာချိန် စောင့်ရန်)
    time.sleep(30)
    
    while True:
        try:
            if not RAW_ID:
                print("⚠️ Error: MY_ID environment variable is missing!")
            else:
                prices = get_market_prices()
                if prices:
                    msg = (f"📊 <b>Market Update</b>\n\n"
                           f"₿ <b>BTC:</b> <code>{prices['BTC']}</code>\n"
                           f"Ξ <b>ETH:</b> <code>{prices['ETH']}</code>")
                    
                    # ID ကို Integer သေချာပြောင်းပြီး ပို့ခြင်း
                    bot.send_message(int(RAW_ID), msg, parse_mode='HTML')
                    print(f"✅ Successfully sent update to {RAW_ID}")
                else:
                    print("⚠️ Could not fetch prices to send.")
        
        except Exception as e:
            print(f"❌ Loop Error: {e}")
        
        # ၁ နာရီ (၃၆၀၀ စက္ကန့်) စောင့်မည်
        print("Waiting for next hour...")
        time.sleep(3600)

# 5. Bot Commands (/price)
@bot.message_handler(commands=['price'])
def send_price(message):
    print(f"Received /price command from {message.chat.id}")
    prices = get_market_prices()
    if prices:
        msg = f"📊 <b>Current Prices</b>\n\nBTC: {prices['BTC']}\nETH: {prices['ETH']}"
        bot.reply_to(message, msg, parse_mode='HTML')
    else:
        bot.reply_to(message, "⚠️ စျေးနှုန်းဆွဲယူ၍ မရနိုင်သေးပါ။ ခဏနေမှ ပြန်ကြိုးစားပါ။")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot အလုပ်လုပ်နေပါပြီ! သင့်ရဲ့ ID က " + str(message.chat.id) + " ဖြစ်ပါတယ်။")

# 6. Main Execution
if __name__ == "__main__":
    # Web Server ကို နောက်ကွယ်မှာ Run မည်
    threading.Thread(target=run_web, daemon=True).start()
    
    # Auto Update Loop ကို နောက်ကွယ်မှာ Run မည်
    threading.Thread(target=auto_send_loop, daemon=True).start()
    
    print("🚀 Bot is starting polling...")
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"❌ Polling Error: {e}")
