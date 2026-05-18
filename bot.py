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
                world_news = "• Brent ရေနံဈေး $110.50 နှင့် WTI $106.20 အထိ မြင့်တက်လာပြီး ဈေးကွက်အရှိန်ကောင်းနေ။"
                local_news = "• QR/Bar Code စနစ်ကို ပဲခူးနှင့် မကွေးလမ်းတလျှောက် မြို့များတွင်ပါ တိုးချဲ့ဆောင်ရွက်။"
                crypto_news = "• BTC $75,000 ဝန်းကျင်တွင် ထိန်းနေပြီး ETH မှာ $1,950 ဝန်းကျင်တွင် ရှိနေ။"
                
                msg = f"📊 <b>Market Update</b>\n<code>BTC: {prices['BTC']}\nETH: {prices['ETH']}\nGold: {prices['Gold']}\nOil: {prices['Oil']}</code>\n\n🌍 <b>World News:</b> {world_news}\n🇲🇲 <b>Local News:</b> {local_news}"
                
                bot.send_message(MY_ID, msg, parse_mode='HTML')
            time.sleep(3600)
        except:
            time.sleep(60)

if __name__ == "__main__":
    # စာကြောင်းအစီအစဉ် မှန်အောင် ပြင်ထားပါတယ်
    threading.Thread(target=auto_send_loop, daemon=True).start()
    print("Bot is starting...")
    bot.infinity_polling()
