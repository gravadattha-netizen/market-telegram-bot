import telebot
import time
import threading
import requests
import os
import google.generativeai as genai

# ၁။ Key များကို Render မှ ဆွဲယူခြင်း
TOKEN = os.getenv('BOT_TOKEN')
MY_ID = os.getenv('MY_ID') 
GEMINI_KEY = os.getenv('GEMINI_KEY')

bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

# ၂။ ဈေးနှုန်းဆွဲယူသည့် Function
def get_market_prices():
    try:
        res = requests.get('https://api.binance.com/api/v3/ticker/price', params={'symbols': '["BTCUSDT","ETHUSDT"]'}, timeout=15).json()
        prices = {item['symbol']: float(item['price']) for item in res}
        f_res = requests.get('https://fapi.binance.com/fapi/v1/ticker/price', timeout=15).json()
        f_prices = {item['symbol']: float(item['price']) for item in f_res if item['symbol'] in ['XAUUSDT', 'CLUSDT']}
        return {
            "BTC": f"${prices.get('BTCUSDT', 0):,.2f}",
            "ETH": f"${prices.get('ETHUSDT', 0):,.2f}",
            "Gold": f"${f_prices.get('XAUUSDT', 0):,.2f}",
            "Oil": f"${f_prices.get('CLUSDT', 0):,.2f}"
        }
    except: return None

# ၃။ ၁ နာရီတစ်ခါ အလိုအလျောက်ပို့ပေးမည့် Loop
def auto_send_loop():
    while True:
        try:
            prices = get_market_prices()
            if prices:
                msg = f"📊 <b>Market Update</b>\n\n<code>BTC: {prices['BTC']}\nETH: {prices['ETH']}\nGold: {prices['Gold']}\nOil: {prices['Oil']}</code>"
                bot.send_message(MY_ID, msg, parse_mode='HTML')
            time.sleep(3600) # ၃၆၀၀ စက္ကန့် (၁ နာရီ) ခြားစီပို့မည်
        except: time.sleep(60)

# ၄။ Commands များ
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါ! Market Bot နိုးနေပါပြီ။ ၁ နာရီတစ်ခါ ဈေးနှုန်းတွေ ပို့ပေးပါမယ်။")

# ၅။ AI နဲ့ စကားပြောဖို့ (မလိုရင် ဖြုတ်ထားနိုင်ပါတယ်)
@bot.message_handler(func=lambda message: True)
def chat_ai(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except: pass

# ၆။ Bot စတင်လည်ပတ်ခြင်း
if __name__ == "__main__":
    threading.Thread(target=auto_send_loop, daemon=True).start()
    bot.infinity_polling()
