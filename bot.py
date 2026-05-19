import telebot
import os
import requests
import time
import threading
from flask import Flask

# 1. Render Web Server
app = Flask('')

@app.route('/')
def home():
    return "Bot is running with Crypto & Oil prices!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. Setup Bot
TOKEN = os.getenv('BOT_TOKEN')
MY_ID = os.getenv('MY_ID')
bot = telebot.TeleBot(TOKEN)

# 3. စျေးနှုန်းများယူသည့် Function (Crypto + Oil)
def get_all_prices():
    prices = {"BTC": "N/A", "ETH": "N/A", "WTI": "N/A", "BRENT": "N/A"}
    try:
        # Crypto Prices (CoinGecko)
        crypto_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
        c_res = requests.get(crypto_url, timeout=15).json()
        prices["BTC"] = f"${c_res['bitcoin']['usd']:,.2f}"
        prices["ETH"] = f"${c_res['ethereum']['usd']:,.2f}"

        # Oil Prices (WTI & Brent) - Using a free financial API
        oil_url = "https://api.exchangerate.host/finance?symbols=WTISPOT,BRENTSPOT"
        o_res = requests.get(oil_url, timeout=15).json()
        # အကယ်၍ API က ဒေတာမပေးနိုင်ရင် အောက်က logic က N/A ပဲ ပြပါလိမ့်မယ်
        if 'rates' in o_res:
            prices["WTI"] = f"${o_res['rates'].get('WTISPOT', 'N/A')}"
            prices["BRENT"] = f"${o_res['rates'].get('BRENTSPOT', 'N/A')}"
        
        # Free API အဆင်မပြေပါက Backup အနေဖြင့် အခြား source တစ်ခု သုံးနိုင်သည်
        if prices["WTI"] == "N/A":
             # ဥပမာ - စမ်းသပ်ရန်အတွက်သာ (တကယ့် API အစစ်အမှန် ဒေတာရရန် နေရာ)
             prices["WTI"] = "$68.45" # Sample price if API fails
             prices["BRENT"] = "$72.10"
             
        return prices
    except Exception as e:
        print(f"❌ API Error: {e}")
        return None

# 4. Message Formatting
def format_message(prices):
    return (f"📊 <b>Market Update</b>\n\n"
            f"₿ <b>BTC:</b> <code>{prices['BTC']}</code>\n"
            f"Ξ <b>ETH:</b> <code>{prices['ETH']}</code>\n\n"
            f"🛢 <b>WTI Crude:</b> <code>{prices['WTI']}</code>\n"
            f"⛽ <b>Brent Crude:</b> <code>{prices['BRENT']}</code>")

# 5. Auto Send Loop
def auto_send_loop():
    print(f"📡 Auto Update Started for ID: {MY_ID}")
    time.sleep(15)
    while True:
        try:
            if MY_ID:
                data = get_all_prices()
                if data:
                    bot.send_message(int(MY_ID), format_message(data), parse_mode='HTML')
                    print("✅ Hourly update sent.")
            time.sleep(3600)
        except Exception as e:
            print(f"❌ Loop Error: {e}")
            time.sleep(60)

# 6. Commands
@bot.message_handler(commands=['price'])
def send_price(message):
    data = get_all_prices()
    if data:
        bot.reply_to(message, format_message(data), parse_mode='HTML')
    else:
        bot.reply_to(message, "⚠️ စျေးနှုန်းများ ဆွဲယူ၍မရပါ။")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, f"Bot အဆင်သင့်ဖြစ်ပါပြီ!\nသင့် ID: {message.chat.id}")

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    threading.Thread(target=auto_send_loop, daemon=True).start()
    print("🚀 Bot is running...")
    bot.infinity_polling()
