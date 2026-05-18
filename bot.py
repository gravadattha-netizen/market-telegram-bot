import telebot
import time
import threading
import warnings
import requests
import os

warnings.filterwarnings("ignore")

# Render Environment Variables
TOKEN = os.getenv('BOT_TOKEN')
MY_ID = os.getenv('MY_ID')

bot = telebot.TeleBot(TOKEN)

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
    except:
        return None

def auto_send_loop():
    while True:
        try:
            prices = get_market_prices()
            if prices:
                msg = f"📊 <b>Market Update</b>\n<code>BTC: {prices['BTC']}\nETH: {prices['ETH']}\nGold: {prices['Gold']}\nOil: {prices['Oil']}</code>"
                bot.send_message(MY_ID, msg, parse_mode='HTML')
            time.sleep(3600) # ၁ နာရီတစ်ခါပို့မယ်
        except:
            time.sleep(60)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot အလုပ်လုပ်နေပါပြီခင်ဗျာ။")

if __name__ == "__main__":
    # ဒီနေရာက space တွေကို အတိအကျ ထားပေးပါ
    threading.Thread(target=auto_send_loop, daemon=True).start()
    print("Bot is starting...")
    bot.infinity_polling()
