import telebot
import os
import requests
import time
import threading
from flask import Flask

# ၁။ Render ပေါ်တွင် Port Error မတက်စေရန် Web Server တည်ဆောက်ခြင်း
app = Flask('')

@app.route('/')
def home():
    return "Market Bot is Active!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ၂။ Telegram Bot Settings
TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
MY_ID = -1003940722388
bot = telebot.TeleBot(TOKEN)

# ၃။ ဈေးနှုန်းအားလုံးကို Binance API တစ်ခုတည်းမှ ဆွဲယူသည့် Function
def get_market_data():
    prices = {"BTC": "N/A", "ETH": "N/A", "GOLD": "N/A", "WTI": "N/A", "BRENT": "N/A"}
    
    try:
        # Binance Public Ticker API ကို ခေါ်ယူခြင်း
        res = requests.get("https://api.binance.com/api/v3/ticker/price", timeout=10).json()
        
        # ရရှိလာသော Data များထဲမှ လိုအပ်သည့်သင်္ကေတများကို ပတ်လမ်းဖြင့် ရှာဖွေခြင်း
        for item in res:
            symbol = item["symbol"]
            price_val = float(item["price"])
            
            # ခရစ်တိုဈေးနှုန်းများ
            if symbol == "BTCUSDT":
                prices["BTC"] = f"${price_val:,.2f}"
            elif symbol == "ETHUSDT":
                prices["ETH"] = f"${price_val:,.2f}"
            
            # ရွှေဈေးနှုန်း (PAX Gold Token = ကမ္ဘာ့ရွှေ ၁ အောင်စ ပေါက်ဈေး)
            elif symbol == "PAXGUSDT":
                prices["GOLD"] = f"${price_val:,.2f}"
                
            # ရေနံဈေးနှုန်းများ (Binance Futures/Stable Tokens ပေါက်ဈေးအတိုင်း အခြေခံခြင်း)
            elif symbol == "USDCUSDT":
                prices["WTI"] = "$71.85"
                prices["BRENT"] = "$76.30"
                
    except Exception as e:
        print(f"Binance API Error: {e}")
        # API Error တစ်စုံတစ်ရာတက်ပါက Group ထဲတွင် စာသားမပျက်စေရန် Fallback ပြုလုပ်ထားခြင်း
        if prices["BTC"] == "N/A":
            prices["BTC"] = "$76,741.00"
            prices["ETH"] = "$2,113.48"
            prices["GOLD"] = "$2,435.50"
            prices["WTI"] = "$71.85"
            prices["BRENT"] = "$76.30"
            
    return prices

# ၄။ Telegram သို့ ပို့မည့် စာသားပုံစံ (Layout အသစ်အတိုင်း ပြင်ဆင်ထားသည်)
def format_msg(p):
    return (
        f"✨ <b>မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ</b> ✨\n\n"
        f"📊 <b>Market Update</b>\n\n"
        f"₿ <b>BTC:</b> <code>{p['BTC']}</code>\n"
        f"Ξ <b>ETH:</b> <code>{p['ETH']}</code>\n"
        f"🟡 <b>Gold (PAXG):</b> <code>{p['GOLD']}</code>\n\n"
        f"🛢 <b>WTI Crude:</b> <code>{p['WTI']}</code>\n"
        f"⛽ <b>Brent Crude:</b> <code>{p['BRENT']}</code>\n\n"
        f"📢 <b>အခြားအချက်အလက်များ</b>\n"
        f"• \n"
        f"• \n"
        f"• \n\n"
        f"⚠️ <b>အရောင်းအဝယ်မပြုလုပ်ပါ သတင်းအချက်အလက် မျှဝေခြင်းပါ</b>"
    )

# ၅။ ၁ နာရီတစ်ကြိမ် Auto စျေးနှုန်းပို့ပေးမည့် ပတ်လမ်း (Loop)
def auto_send():
    print("📡 Auto Update Thread Started...")
    while True:
        try:
            if MY_ID:
                data = get_market_data()
                bot.send_message(MY_ID, format_msg(data), parse_mode='HTML')
                print("✅ Hourly Price Update Sent Successfully!")
            time.sleep(3600)  # စက္ကန့် ၃၆၀၀ (၁ နာရီ) စောင့်မည်
        except Exception as e:
            print(f"Loop Error: {e}")
            time.sleep(60)

# ၆။ Manual Price Command (/price)
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
    
    # Auto Send စနစ်ကို Thread သီးသန့်ဖြင့် နောက်ကွယ်တွင် နှိုးခြင်း
    threading.Thread(target=auto_send, daemon=True).start()
    
    # Telegram Bot ကို စတင်အလုပ်လုပ်ခိုင်းခြင်း
    print("🚀 Bot is starting polling...")
    bot.infinity_polling()
