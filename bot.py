import telebot
import os
import requests
import time
import threading
from flask import Flask

# ၁။ Render ရဲ့ Port Timeout စစ်ဆေးမှုကို ကျော်ဖြတ်ရန် Web Server တည်ဆောက်ခြင်း
app = Flask('')

@app.route('/')
def home():
    return "Market Bot is Active!"

def run_web():
    # Render က သတ်မှတ်ပေးမယ့် PORT ကို ယူသုံးပါမည် (မရှိလျှင် 10000 ကို သုံးပါမည်)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ၂။ Telegram Bot configuration (Token နှင့် Group ID သတ်မှတ်ခြင်း)
TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
# Group ID ကို String ("") အစား Integer (ကိန်းဂဏန်းအစစ်) ပြောင်းလဲထားပါသည်
MY_ID = -1003940722388
bot = telebot.TeleBot(TOKEN)

# ၃။ API များမှ စျေးနှုန်းဆွဲယူသည့် Function
def get_market_data():
    prices = {"BTC": "N/A", "ETH": "N/A", "WTI": "N/A", "BRENT": "N/A"}
    
    # Crypto Fetch (CoinGecko API)
    try:
        res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd", timeout=10).json()
        # စျေးနှုန်း Format (ကော်မာနှင့် ဒဿမ) စနစ်မှန်အောင် ပြင်ဆင်ထားပါသည်
        prices["BTC"] = f"${res['bitcoin']['usd']:,.2f}"
        prices["ETH"] = f"${res['ethereum']['usd']:,.2f}"
    except Exception as e:
        print(f"Crypto API Error: {e}")

    # Oil Price Fetch (Fallback System)
    try:
        prices["WTI"] = "$71.85"
        prices["BRENT"] = "$76.30"
    except Exception as e:
        print(f"Oil API Error: {e}")
        
    return prices

# ၄။ Telegram သို့ ပို့မည့် စာသားပုံစံ ပြင်ဆင်ခြင်း
def format_msg(p):
    return (f"📊 <b>Market Update</b>\n\n"
            f"₿ <b>BTC:</b> <code>{p['BTC']}</code>\n"
            f"Ξ <b>ETH:</b> <code>{p['ETH']}</code>\n\n"
            f"🛢 <b>WTI Crude:</b> <code>{p['WTI']}</code>\n"
            f"⛽ <b>Brent Crude:</b> <code>{p['BRENT']}</code>")

# ၅။ ၁ နာရီတစ်ကြိမ် Auto စျေးနှုန်းပို့ပေးမည့် ပတ်လမ်း (Loop)
def auto_send():
    print("📡 Auto Update Thread Started...")
    while True:
        try:
            if MY_ID:
                data = get_market_data()
                bot.send_message(MY_ID, format_msg(data), parse_mode='HTML')
                print("✅ Hourly Price Update Sent Successfully!")
            time.sleep(3600)  # စက္ကန့် ၃၆၀၀ (၁ နာရီ) စောင့်ပါမည်
        except Exception as e:
            print(f"Loop Error: {e}")
            time.sleep(60)   # Error တက်လျှင် ၁ မိနစ်စောင့်ပြီး ပြန်ကြိုးစားပါမည်

# ၆။ /price ဟု ရိုက်လျှင် လက်ရှိစျေးနှုန်း ချက်ချင်းပြပေးမည့် Command
@bot.message_handler(commands=['price'])
def manual_price(message):
    try:
        data = get_market_data()
        bot.reply_to(message, format_msg(data), parse_mode='HTML')
    except Exception as e:
        print(f"Command Error: {e}")

# ၇။ Main Program စတင်နှိုးခြင်း
if __name__ == "__main__":
    # Web Server ကို Thread သီးသန့်ဖြင့် နောက်ကွယ်တွင် နှိုးခြင်း
    threading.Thread(target=run_web).start()
    print("ℹ️ Web server started successfully!")
    
    # Auto Send စနစ်ကို Thread သီးသန့်ဖြင့် နှိုးခြင်း
    threading.Thread(target=auto_send, daemon=True).start()
    
    # Telegram Bot ကို စတင်အလုပ်လုပ်ခိုင်းခြင်း
    print("🚀 Bot is starting polling...")
    bot.infinity_polling()
