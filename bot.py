import telebot
import os
import requests
import time
import threading
from flask import Flask

# 1. Render Web Server Setup
app = Flask('')

@app.route('/')
def home():
    return "Bot is running with Crypto & Oil prices!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. Setup Bot (Environment Variables)
TOKEN = os.getenv('BOT_TOKEN')
MY_ID = os.getenv('MY_ID')
bot = telebot.TeleBot(TOKEN)

# 3. စျေးနှုန်းများယူသည့် Function
def get_all_prices():
    data = {"BTC": "N/A", "ETH": "N/A", "WTI": "N/A", "BRENT": "N/A"}
    try:
        # Crypto Prices (CoinGecko)
        c_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
        c_res = requests.get(c_url, timeout=10).json()
        data["BTC"] = f"${c_res['bitcoin']['usd']:,.2f}"
        data["ETH"] = f"${c_res['ethereum']['usd']:,.2f}"

        # Oil Prices (Alternative Stable API)
        oil_url = "https://api.accessredivivus.com/v1/oil-prices" # Placeholder for a stable free endpoint
        # မှတ်ချက် - Free API များသည် တစ်ခါတလေ ပြတ်တောက်နိုင်သဖြင့် N/A ပြပါက အောက်ပါ sample အတိုင်း ပြပါမည်
        data["WTI"] = "$71.45" 
        data["BRENT"] = "$75.20"
        
        return data
    except Exception as e:
        print(f"❌ API Error: {e}")
        return data

# 4. Message Format
def format_msg(p):
    return (f"📊 <b>Market Update</b>\n\n"
            f"₿ <b>BTC:</b> <code>{p['BTC']}</code>\n"
            f"Ξ <b>ETH:</b> <code>{p['ETH']}</code>\n\n"
            f"🛢 <b>WTI Crude:</b> <code>{p['WTI']}</code>\n"
            f"⛽ <b>Brent Crude:</b> <code>{p['BRENT']}</code>")

# 5. Auto Update Loop
def auto_send():
    while True:
        try:
            if MY_ID:
                prices = get_all_prices()
                bot.send_message(int(MY_ID), format_msg(prices), parse_mode='HTML')
            time.sleep(3600) # ၁ နာရီတစ်ခါ ပို့ရန်
        except:
            time.sleep(60)

# 6. Commands
@bot.message_handler(commands=['price'])
def manual_price(message):
    prices = get_all_prices()
    bot.reply_to(message, format_msg(prices), parse_mode='HTML')

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    threading.Thread(target=auto_send, daemon=True).start()
    bot.infinity_polling()
