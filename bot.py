import os
import time
import requests
import threading
from flask import Flask
import telebot

app = Flask('')

@app.route('/')
def home():
    return "Market Bot is Active!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Token နှင့် Chat ID (တိုက်ရိုက် အမှန်ပြင်ဆင်ထားသည်)
TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
MY_ID = "-1003940722388"
bot = telebot.TeleBot(TOKEN)

def get_market_data():
    prices = {"BTC": "N/A", "ETH": "N/A", "GOLD": "N/A", "WTI": "N/A", "BRENT": "N/A"}
    symbols = {
        "BTCUSDT": "BTC",
        "ETHUSDT": "ETH",
        "PAXGUSDT": "GOLD",
        "CLUSDT": "WTI",
        "BZUSDT": "BRENT"
    }
    try:
        # Binance Public API မှ စျေးနှုန်းများ တိုက်ရိုက်ဆွဲယူခြင်း
        res = requests.get("https://api.binance.com/api/v3/ticker/price", timeout=10).json()
        for item in res:
            sym = item['symbol']
            if sym in symbols:
                price_val = float(item['price'])
                prices[symbols[sym]] = f"${price_val:,.2f}"
    except Exception as e:
        print(f"Binance API Error: {e}")
    return prices

def send_update():
    prices = get_market_data()
    
    # အစ်ကိုတောင်းဆိုထားသည့် စာသားပုံစံအတိုင်း ပြင်ဆင်ခြင်း
    text = (
        f"🌟 **မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ** 🌟\n\n"
        f"📊 **Market Update**\n\n"
        f"₿ BTC: {prices['BTC']}\n"
        f"Ξ ETH: {prices['ETH']}\n"
        f"🟡 Gold (PAXG): {prices['GOLD']}\n"
        f"⛽ WTI Crude: {prices['WTI']}\n"
        f"🛢 Brent Crude: {prices['BRENT']}\n\n"
        f"📢 **အခြားအချက်အလက်များ**\n"
        f"• \n"
        f"• \n"
        f"• \n\n"
        f"⚠️ _အရောင်းအဝယ်မပြုလုပ်ပါ သတင်းအချက်အလက် မျှဝေခြင်းပါ_"
    )
    
    try:
        bot.send_message(MY_ID, text, parse_mode="Markdown")
        print("Message sent successfully!")
    except Exception as e:
        print(f"Send Message Error: {e}")

def auto_update_worker():
    print("Auto Update Thread Started...")
    # စက်နိုးနိုးချင်း ၅ စက္ကန့်အတွင်း Group ထဲကို စာအရင်ဆုံး ပို့လိုက်မည်
    time.sleep(5)
    send_update()
    
    # ထို့နောက်ပိုင်းတွင်မှ ၁ နာရီ (၃၆၀၀ စက္ကန့်) တစ်ခါ ပုံမှန် အော်တိုပတ်သွားမည်
    while True:
        time.sleep(3600)
        send_update()

@bot.message_handler(commands=['price'])
def manual_price(message):
    send_update()

if __name__ == "__main__":
    # Web Server ပတ်ခြင်း
    t_web = threading.Thread(target=run_web)
    t_web.daemon = True
    t_web.start()
    
    # အော်တို Update အတွက် Thread ပတ်ခြင်း
    t_auto = threading.Thread(target=auto_update_worker)
    t_auto.daemon = True
    t_auto.start()
    
    print("Bot is starting polling...")
    bot.infinity_polling()
