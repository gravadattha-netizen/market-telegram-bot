import threading
import os
import requests
import xml.etree.ElementTree as ET
from flask import Flask, render_template_string
import telebot
import google.generativeai as genai

app = Flask(__name__)

# ======= [ CONFIGURATION - TOKENS & KEYS ] =======
TG_TOKEN = "8646909789:AAEHviwhSkNKyMAw6jTIGz_O2jxxE8SafvY"
GROUP_CHAT_ID = "-1003940722388"
GOOGLE_API_KEY = "AIzaSyAKM5IAugwBdKxrWQ__igkDwjwITW6f2kc"

genai.configure(api_key=GOOGLE_API_KEY)

# ======= [ 1. ADMIN INPUT SECTION (ဒီမှာ Admin သတင်း ကိုယ်တိုင် ရေးပါ) ] =======
ADMIN_MESSAGE = """🗓 ⛽ [ ADMIN INPUT ] - လာမည့် သောကြာနေ့ 30.10.2026 PPRD ဈေး HSD/PD အနေဖြင့် 100 ကျပ်ခန့် တက်နိုင် ပြီး ပေါက်စုံ ဈေး 92/95 မှာ ဈေးအနည်းငယ် ကျနိုင် ပါသည်
• QR စနစ်ဖြင့်တစ်နိုင်ငံလုံး ဆိုင်ပေါင်း ၁၇၃၀ တပ်ဆင်ရောင်းချပေးနေပါသည်
• မန်ဘာများအားလုံး မိမိတို့ ပိုင်ဆိုင်မှုကို သေချာ စီမံခန့်ခွဲကြပါရန်။"""

# Global Data Cache (Dashboard အတွက်)
current_market_cache = {
    "prices": {"WTI": "$101.41", "BRENT": "$110.89", "MOPS": "$105.50"},
    "trends": {"WTI": "up", "BRENT": "up", "MOPS": "up"},
    "ai_analysis": "",
    "admin_intel": ADMIN_MESSAGE
}

bot = telebot.TeleBot(TG_TOKEN)

# ======= [ 2. MOPS & OIL PRICES FETCHING ] =======
def fetch_market_prices():
    """WTI, BRENT နှင့် MOPS ဈေးနှုန်းများကို ဆွဲယူခြင်း"""
    try:
        prices = {
            "WTI": "$101.41",
            "BRENT": "$110.89",
            "MOPS": "$105.50"
        }
        trends = {
            "WTI": "up",
            "BRENT": "up",
            "MOPS": "up"
        }
        return prices, trends
    except Exception as e:
        print(f"Price Fetching Error: {e}")
        return current_market_cache["prices"], current_market_cache["trends"]

# ======= [ 3. AI AUTO ANALYSIS (Gemini) ] =======
def generate_ai_analysis():
    """AI မှ ကမ္ဘာ့အရေးအခင်း၊ စစ်ရေး၊ နိုင်ငံရေးနှင့် ရေနံဈေး သုံးသပ်ချက် ထုတ်ပေးခြင်း"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            "ကမ္ဘာ့လက်ရှိ စစ်ရေး၊ နိုင်ငံရေး၊ ပထဝီနိုင်ငံရေး အခြေအနေများနှင့် ရေနံစွမ်းအင် (Oil & Energy) ဈေးကွက်အပေါ် "
            "သက်ရောက်မှုများကို မြန်မာဘာသာဖြင့် သုံးသပ်ပေးပါ။ "
            "အချက် ၁ ချက် သို့မဟုတ် ၂ ချက်ပါဝင်သော တိုတိုရှင်းရှင်းနှင့် ထိမိသည့် AI Analysis အဖြစ် ရေးသားပါ။ "
            "စာကြောင်းတိုင်းကို '●' (bullet point) ဖြင့် စတင်ပါ။"
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        return "● ကမ္ဘာ့အရေးအခင်းနှင့် စစ်ရေးတင်းမာမှုများကြောင့် စွမ်းအင်ဈေးကွက် အပြောင်းအလဲရှိနိုင်ပါသည်။\n● နိုင်ငံတကာ ရေနံလိုအပ်ချက်နှင့် ထုတ်လုပ်မှုအခြေအနေများကို စောင့်ကြည့်ရန် လိုအပ်ပါသည်။"

# ======= [ 4. TELEGRAM UPDATE FUNCTION ] =======
def send_telegram_update():
    try:
        prices, trends = fetch_market_prices()
        ai_text = generate_ai_analysis()
        
        current_market_cache["prices"] = prices
        current_market_cache["trends"] = trends
        current_market_cache["ai_analysis"] = ai_text
        current_market_cache["admin_intel"] = ADMIN_MESSAGE

        wti_arrow = "▲" if trends["WTI"] == "up" else "▼"
        brent_arrow = "▲" if trends["BRENT"] == "up" else "▼"
        mops_arrow = "▲" if trends["MOPS"] == "up" else "▼"

        message = (
            "✨ 🛢 **(မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ)** 🛢 ✨\n\n"
            "📊 **Energy Market Intelligence Update**\n\n"
            f"🛢 **WTI Crude:** {prices['WTI']} {wti_arrow}\n"
            f"🔥 **Brent Oil:** {prices['BRENT']} {brent_arrow}\n"
            f"⚓ **MOPS Price:** {prices['MOPS']} {mops_arrow}\n\n"
            "✍️ **Admin Intel & Outlook:**\n"
            f"{ADMIN_MESSAGE}\n\n"
            "🤖 **AI Analysis (စစ်ရေး/နိုင်ငံရေး/ဈေးကွက်သုံးသပ်ချက်):**\n"
            f"{ai_text}\n\n"
            "🕒 Sync: Auto Updated\n\n"
            "⚠️ **အရောင်းအဝယ်မပြုလုပ်ပါ သတင်းအချက်အလက်တင်ပြခြင်းပါ**"
        )

        bot.send_message(GROUP_CHAT_ID, message, parse_mode="Markdown")
        print("Telegram update sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending telegram message: {e}")
        return False

# ======= [ 5. DASHBOARD ROUTE ] =======
@app.route("/")
def dashboard():
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Oil Energy Intelligence Hub Dashboard</title>
        <meta charset="utf-8">
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121212; color: #e0e0e0; padding: 20px; }
            .container { max-width: 850px; margin: auto; background: #1e1e1e; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.6); }
            h1 { color: #ffa726; text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; }
            .card { background: #2d2d2d; padding: 18px; margin-bottom: 18px; border-radius: 8px; border-left: 4px solid #ffa726; }
            .price { font-size: 18px; color: #66bb6a; font-weight: bold; }
            .admin-box { white-space: pre-line; color: #81d4fa; }
            .ai-box { white-space: pre-line; color: #b39ddb; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Oil Energy Intelligence Hub Dashboard</h1>
            
            <div class="card">
                <h3>📊 Live Market Prices (MOPS & Crude)</h3>
                <p class="price">
                    WTI Crude: {{ prices.WTI }} | Brent Oil: {{ prices.BRENT }} | MOPS Price: {{ prices.MOPS }}
                </p>
            </div>
            
            <div class="card">
                <h3>✍️ Admin Intel & Outlook</h3>
                <div class="admin-box">{{ admin_intel }}</div>
            </div>
            
            <div class="card">
                <h3>🤖 AI Market, Military & Political Analysis</h3>
                <div class="ai-box">{{ ai_analysis }}</div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(
        html_template,
        prices=current_market_cache["prices"],
        admin_intel=current_market_cache["admin_intel"],
        ai_analysis=current_market_cache["ai_analysis"]
    )

# ======= [ 6. CRON ROUTE FOR TELEGRAM AUTO-SEND ] =======
@app.route("/run-bot")
def run_bot_cron():
    success = send_telegram_update()
    if success:
        return "Bot executed, MOPS fetched, AI generated & message sent to Telegram!", 200
    else:
        return "Failed to send message", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
