import time
import requests
import threading
import os
import re
import xml.etree.ElementTree as ET
from flask import Flask, render_template_string, request, jsonify # jsonify နှင့် request ထည့်သွင်း
import telebot
import google.generativeai as genai

app = Flask('')

# ======= [ CONFIGURATION - TOKENS & KEYS ] =======
TG_TOKEN = "8646909789:AAFhLamWEWkqjnCd2pfjEXn5lMoBWPCejNo" 
GROUP_CHAT_ID = -1003940722388  
GOOGLE_API_KEY = "AIzaSyAKM5IAugwBdKxrWQ__igkDwjwITW6f2kc"

genai.configure(api_key=GOOGLE_API_KEY)

# =========================================================
# ✍️ [ ADMIN INPUT ]
# =========================================================
ADMIN_MESSAGE = """●QR စနစ်ဖြင့်တစ်နိုင်ငံလုံး ဆိုင်ပေါင်း ၁၇၃၀ တပ်ဆင်ရောင်းချ ပေးနေပါသည်
● ရွှေဈေးကတော့ ကမ္ဘာ့ဒေါ်လာအညွှန်းကိန်း (DXY) ကြောင့် အနည်းငယ် ပြန်ဆင်းနိုင်ပါတယ်။
● မန်ဘာများအားလုံး မိမိတို့ ပိုင်ဆိုင်မှုကို သေချာ စီမံခန့်ခွဲကြပါရန်။"""

# Global Data Cache
current_market_cache = {
    "prices": {"BTC": 0.0, "ETH": 0.0, "GOLD": 0.0, "WTI": 0.0, "BRENT": 0.0, "DXY": 0.0},
    "display_prices": {"BTC": "$0.00", "ETH": "$0.00", "GOLD": "$0.00", "WTI": "$0.00", "BRENT": "$0.00", "DXY": "0.00"},
    "trends": {"BTC": "neutral", "ETH": "neutral", "GOLD": "neutral", "WTI": "neutral", "BRENT": "neutral", "DXY": "neutral"},
    "last_update": "N/A",
    "crypto_gauge": 50, "wti_gauge": 50, "brent_gauge": 50, "gold_gauge": 50,
    "ai_news": "● ကမ္ဘာ့စီးပွားရေးနှင့် ရေနံဈေးကွက်သတင်းများကို AI ဖြင့် သေချာစွာ အနှစ်ချုပ် သုံးသပ်နေပါသည်...",
    "last_mops_text": "No custom MOPS news forwarded yet.",
    "admin_intel": ADMIN_MESSAGE 
}

# (Dashboard HTML Code သည် အရင်အတိုင်း ထားပါ)
DASHBOARD_HTML = """...""" # အစ်ကို့ဆီက ရှိတဲ့ HTML ကို ဒီအတိုင်းထားပါ

@app.route('/')
def home():
    return render_template_string(DASHBOARD_HTML, data=current_market_cache)

# ======= [ NEW: n8n WEBHOOK ENDPOINT ] =======
@app.route('/receive-news', methods=['POST'])
def receive_news():
    try:
        data = request.json
        news_content = data.get('news', 'သတင်းအချက်အလက် မရှိပါ။')
        # n8n ကပို့တဲ့သတင်းကို Cache ထဲ update လုပ်
        current_market_cache["last_mops_text"] = news_content
        return jsonify({"status": "Success", "message": "Updated successfully"})
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500

# ======= [ REST OF THE CODE ] =======
# (update_ai_analysis, get_market_data, update_dashboard_data, 
# generate_telegram_msg, bot.message_handler, bot.polling များအားလုံးကို ဒီအတိုင်း ဆက်ထားပါ)

bot = telebot.TeleBot(TG_TOKEN)

# (အောက်က code အပိုင်းများလည်း မူလအတိုင်း ဆက်ထားပါ)
if __name__ == "__main__":
    update_dashboard_data()
    current_market_cache["ai_news"] = update_ai_analysis(current_market_cache["prices"])
    
    threading.Thread(target=dashboard_loop, daemon=True).start()
    threading.Thread(target=telegram_loop, daemon=True).start()
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    
    while True:
        try: bot.polling(none_stop=True)
        except: time.sleep(5)
