import telebot
import time
import threading
import warnings
import requests

warnings.filterwarnings("ignore")

TOKEN = '8646909789:AAFXY7E8-KPzmdfXt0QkRQVZjy3iwdVhglE'
MY_ID = '-1003940722388' 

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
    except: return None

def auto_send_loop():
    while True:
        try:
            prices = get_market_prices()
            if prices:
                world_news = "• Brent ရေနံဈေး $110.50 နှင့် WTI $106.20 အထိ မြင့်တက်လာပြီး ဈေးကွက်အရှိန်ကောင်းနေ။\n• ဟော်မုဇ်ရေလက်ကြား လုံခြုံရေးစိုးရိမ်မှုကြောင့် ရေနံတင်ပို့မှု ပြတ်တောက်နိုင်ခြေရှိနေဆဲ။"
                local_news = "• QR/Bar Code စနစ်ကို ပဲခူးနှင့် မကွေးလမ်းတလျှောက် မြို့များတွင်ပါ တိုးချဲ့ဆောင်ရွက်။\n• ဆီခွဲတမ်းကို မိုင်နှုန်း (Mileage) အပေါ်မူတည်၍ ရောင်းချပေးမည့်စနစ်သို့ ပြောင်းလဲစီစဉ်နေ။"
                crypto_news = "• BTC $75,000 ဝန်းကျင်တွင် ထိန်းနေပြီး ဈေးကွက်ပြန်တက်ရန် အားယူနေသည့်အခြေအနေ။\n• ETH မှာ $1,950 ဝန်းကျင်တွင် Support ရှာနေ။"
                
                msg = f"✨ <b>မင်္ဂလာရှိသော နေ့လေးဖြစ်ပါစေ</b> ✨\n\n📊 <b>Market Update</b>\n<code>BTC: {prices['BTC']}\nETH: {prices['ETH']}\nGold: {prices['Gold']}\nOil: {prices['Oil']}</code>\n\n🌍 <b>ကမ္ဘာ့သတင်း</b>\n<i>{world_news}</i>\n\n🇲🇲 <b>မြန်မာ့သတင်း</b>\n<i>{local_news}</i>\n\n🪙 <b>Crypto Update</b>\n<i>{crypto_news}</i>\n\nℹ️ <i>သတင်းအချက်အလက်အပေါ် အလွဲအမှားရှိရင် Admin ရဲ့ မှားယွင်းမှုပါ။</i>"
                
                bot.send_message(MY_ID, msg, parse_mode='HTML')
            time.sleep(3600)
        except: time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=auto_send_loop, daemon=True).start()
    bot.infinity_polling()
