import telebot
import os
import requests
import time
import threading
from flask import Flask

# 1. Render အတွက် Web Server Setup
app = Flask('')

@app.route('/')
def home():
    return "Bot is running and fetching data from CoinGecko!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. API Keys နှင့် ID ယူခြင်း
TOKEN = os.getenv('BOT_TOKEN')
MY_ID = os.getenv('MY_ID')
bot = telebot.TeleBot(TOKEN)

# 3. Market Price ဆွဲသည့် Function (CoinGecko သုံးထားသည်)
def get_market_prices():
    try:
        # CoinGecko က Cloud Platform တွေကို Block လုပ်လေ့မရှိပါ
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
        response = requests.get(url, timeout=20)
        data = response.json()
        
        btc_price = data['bitcoin']['usd']
        eth_price = data['ethereum']['usd']
        
        return {
            "BTC": f"${btc_price:,.2f}",
            "ETH": f"${eth_price:,.2f}"
        }
    except Exception as e:
        print(f"❌ API Connection Error: {e}")
        return None

# 4. အလိုအလျောက် စျေးနှုန်းပို့ပေးမည့် Loop
def auto_send_loop():
    print(f"📡 Auto Update Thread Started for ID: {MY_ID}")
    time.sleep(15) # Server တက်လာချိန် ခဏစောင့်ခြင်း
    
    while True:
        try:
            if MY_ID:
                prices = get_market_prices()
                if prices:
                    msg = (f"📊 <b>Hourly Market Update</b>\n\n"
                           f"₿ <b>BTC:</b> <code>{prices['BTC']}</code>\n"
                           f"Ξ <b>ETH:</b> <code>{prices['ETH']}</code>")
                    
                    bot.send_message(int(MY_ID), msg, parse_mode='HTML')
                    print(f"✅ Auto update sent to {MY_ID}")
                else:
                    print("⚠️ Could not fetch prices for auto-update.")
            else:
                print("⚠️ MY_ID is missing in Environment Variables!")
        except Exception as e:
            print(f"❌ Loop Error: {e}")
        
        # ၁ နာရီ (၃၆၀၀ စက္ကန့်) စောင့်မည်
        time.sleep(3600)

# 5. Bot Commands (/price နှင့် /start)
@bot.message_handler(commands=['price'])
def send_price(message):
    print(f"User {message.chat.id} asked for price.")
    prices = get_market_prices()
    if prices:
        msg = (f"📊 <b>Current Prices</b>\n\n"
               f"BTC: <b>{prices['BTC']}</b>\n"
               f"ETH: <b>{prices['ETH']}</b>")
        bot.reply_to(message, msg, parse_mode='HTML')
    else:
        bot.reply_to(message, "⚠️ စျေးနှုန်းဆွဲယူရာတွင် အခက်အခဲရှိနေပါသည်။ ခဏနေမှ ပြန်ကြိုးစားပါ။")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, f"Bot အလုပ်လုပ်နေပါပြီ!\nသင့်ရဲ့ ID က {message.chat.id} ဖြစ်ပါတယ်။")

# 6. Bot ကို စတင် Run ခြင်း
if __name__ == "__main__":
    # Web Server ကို Thread တစ်ခုဖြင့် Run ရန်
    threading.Thread(target=run_web).start()
    
    # Auto Loop ကို Thread တစ်ခုဖြင့် Run ရန်
    threading.Thread(target=auto_send_loop, daemon=True).start()
    
    print("🚀 Bot Polling Started...")
    bot.infinity_polling()
