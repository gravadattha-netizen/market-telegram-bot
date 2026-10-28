import threading
import os
import time
import requests
from flask import Flask, render_template_string
import telebot
import google.generativeai as genai

app = Flask(__name__)

# ======= [ CONFIGURATION - TOKENS & KEYS ] =======
TG_TOKEN = "8646909789:AAEHviwhSkNKyMAw6jTIGz_O2jxxE8SafvY"
GROUP_CHAT_ID = "-1003940722388"
GOOGLE_API_KEY = "AIzaSyAKM5IAugwBdKxrWQ__igkDwjwITW6f2kc"

genai.configure(api_key=GOOGLE_API_KEY)

# ======= [ 1. ADMIN INPUT SECTION ] =======
ADMIN_MESSAGE = """🗓 ⛽ [ ADMIN INPUT ] - လာမည့် သောကြာနေ့ 30.10.2026 PPRD ဈေး HSD/PD အနေဖြင့် 100 ကျပ်ခန့် တက်နိုင် ပြီး ပေါက်စုံ ဈေး 92/95 မှာ ဈေးအနည်းငယ် ကျနိုင် ပါသည်
• QR စနစ်ဖြင့်တစ်နိုင်ငံလုံး ဆိုင်ပေါင်း ၁၇၃၀ တပ်ဆင်ရောင်းချပေးနေပါသည်
• မန်ဘာများအားလုံး မိမိတို့ ပိုင်ဆိုင်မှုကို သေချာ စီမံခန့်ခွဲကြပါရန်။"""

# Global Data Cache
current_market_cache = {
    "prices": {
        "WTI": "$101.41", 
        "BRENT": "$110.89", 
        "MOPS_GASOLINE": "$142.50", 
        "MOPS_DIESEL": "$179.20"
    },
    "trends": {
        "WTI": "up", 
        "BRENT": "up", 
        "MOPS_GASOLINE": "up", 
        "MOPS_DIESEL": "up"
    },
    "technical_signal": "Strong Buy",
    "sentiment": {"bullish": 78, "bearish": 22},
    "ai_analysis": "● ကမ္ဘာ့အရေးအခင်းနှင့် စစ်ရေးတင်းမာမှုများကြောင့် စွမ်းအင်ဈေးကွက် အပြောင်းအလဲရှိနိုင်ပါသည်။\n● နိုင်ငံတကာ ရေနံလိုအပ်ချက်နှင့် ထုတ်လုပ်မှုအခြေအနေများကို စောင့်ကြည့်ရန် လိုအပ်ပါသည်။",
    "admin_intel": ADMIN_MESSAGE,
    "last_updated": "Auto Updated"
}

bot = telebot.TeleBot(TG_TOKEN)

# ======= [ 2. MARKET & TECHNICAL DATA FETCHING ] =======
def fetch_live_market_data():
    try:
        prices = {
            "WTI": "$101.41",
            "BRENT": "$110.89",
            "MOPS_GASOLINE": "$142.50",
            "MOPS_DIESEL": "$179.20"
        }
        trends = {
            "WTI": "up",
            "BRENT": "up",
            "MOPS_GASOLINE": "up",
            "MOPS_DIESEL": "up"
        }
        signal = "Strong Buy"  # ပုံထဲပါသည့် Technical Indicator ပုံစံ
        sentiment = {"bullish": 82, "bearish": 18}
        return prices, trends, signal, sentiment
    except Exception as e:
        print(f"Market Fetching Error: {e}")
        return current_market_cache["prices"], current_market_cache["trends"], current_market_cache["technical_signal"], current_market_cache["sentiment"]

# ======= [ 3. AI AUTO ANALYSIS ] =======
def generate_ai_analysis():
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            "ကမ္ဘာ့လက်ရှိ စစ်ရေး၊ နိုင်ငံရေး၊ ပထဝီနိုင်ငံရေး အခြေအနေများနှင့် ဓာတ်ဆီ၊ ဒီဇယ် (MOPS Gasoline & Diesel 10ppm) ဈေးကွက်အပေါ် "
            "သက်ရောက်မှုများကို မြန်မာဘာသာဖြင့် တိုတိုရှင်းရှင်း သုံးသပ်ပေးပါ။ "
            "အချက် ၂ ချက်ပါဝင်သော bullet points (●) များဖြင့်သာ ရေးသားပေးပါ။"
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        return current_market_cache["ai_analysis"]

# ======= [ 4. TELEGRAM UPDATE FUNCTION ] =======
def send_telegram_update():
    try:
        prices, trends, signal, sentiment = fetch_live_market_data()
        ai_text = generate_ai_analysis()
        
        current_market_cache["prices"] = prices
        current_market_cache["trends"] = trends
        current_market_cache[" технический_signal"] = signal
        current_market_cache["sentiment"] = sentiment
        current_market_cache["ai_analysis"] = ai_text
        current_market_cache["admin_intel"] = ADMIN_MESSAGE
        current_market_cache["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")

        wti_status = "BUY ▲" if trends["WTI"] == "up" else "SELL ▼"
        brent_status = "BUY ▲" if trends["BRENT"] == "up" else "SELL ▼"
        gas_status = "BUY ▲" if trends["MOPS_GASOLINE"] == "up" else "SELL ▼"
        diesel_status = "BUY ▲" if trends["MOPS_DIESEL"] == "up" else "SELL ▼"

        message = (
            "✨ 🛢 **(မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ)** 🛢 ✨\n\n"
            "📊 **Energy Market Intelligence Update**\n\n"
            f"🛢 **WTI Crude:** {prices['WTI']} ({wti_status})\n"
            f"🔥 **Brent Oil:** {prices['BRENT']} ({brent_status})\n"
            f"⛽ **MOPS Gasoline (ဓာတ်ဆီ):** {prices['MOPS_GASOLINE']} ({gas_status})\n"
            f"🚛 **MOPS Diesel 10ppm (ဒီဇယ်):** {prices['MOPS_DIESEL']} ({diesel_status})\n\n"
            f"📈 **Technical Indicator:** {signal} 🟢\n"
            f"🐂 **Market Sentiment:** Bullish {sentiment['bullish']}% | Bearish {sentiment['bearish']}%\n\n"
            "✍️ **Admin Intel & Outlook:**\n"
            f"{ADMIN_MESSAGE}\n\n"
            "🤖 **AI & Market Analysis:**\n"
            f"{ai_text}\n\n"
            f"🕒 Sync: {current_market_cache['last_updated']}\n\n"
            "⚠️ **အရောင်းအဝယ်မပြုလုပ်ပါ သတင်းအချက်အလက်တင်ပြခြင်းပါ**"
        )

        bot.send_message(GROUP_CHAT_ID, message, parse_mode="Markdown")
        print("4-hourly telegram update sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending telegram message: {e}")
        return False

# ======= [ 5. BACKGROUND (4-HOURLY) AUTO-UPDATER THREAD ] =======
def auto_update_loop():
    while True:
        # ၄ နာရီလျှင် တစ်ကြိမ် (စက္ကန့် ၁၄၄၀၀ = ၄ နာရီ)
        time.sleep(14400)
        try:
            prices, trends, signal, sentiment = fetch_live_market_data()
            ai_text = generate_ai_analysis()
            current_market_cache["prices"] = prices
            current_market_cache["trends"] = trends
            current_market_cache["technical_signal"] = signal
            current_market_cache["sentiment"] = sentiment
            current_market_cache["ai_analysis"] = ai_text
            current_market_cache["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Telegram သို့ အလိုအလျောက် ပို့မည်
            send_telegram_update()
            print("4-hourly background update executed.")
        except Exception as e:
            print(f"Update thread error: {e}")

# Start background thread
threading.Thread(target=auto_update_loop, daemon=True).start()

# ======= [ 6. DASHBOARD ROUTE ] =======
@app.route("/")
def dashboard():
    prices = current_market_cache["prices"]
    trends = current_market_cache["trends"]
    signal = current_market_cache.get("technical_signal", "Strong Buy")
    sentiment = current_market_cache.get("sentiment", {"bullish": 82, "bearish": 18})
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Oil Energy Intelligence Hub Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            :root {
                --bg-color: #0d1117;
                --card-bg: #161b22;
                --border-color: #30363d;
                --text-main: #c9d1d9;
                --accent-orange: #f0883e;
                --buy-green: #2ea043;
                --sell-red: #da3633;
            }
            body {
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: var(--bg-color);
                color: var(--text-main);
                margin: 0;
                padding: 20px;
            }
            .container {
                max-width: 950px;
                margin: auto;
                background: var(--card-bg);
                padding: 30px;
                border-radius: 16px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.7);
                border: 1px solid var(--border-color);
            }
            h1 {
                color: var(--accent-orange);
                text-align: center;
                margin-bottom: 25px;
                font-size: 26px;
                letter-spacing: 0.5px;
                border-bottom: 2px solid var(--border-color);
                padding-bottom: 15px;
            }
            .card {
                background: #21262d;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 12px;
                border: 1px solid var(--border-color);
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }
            .card h3.center-title {
                margin-top: 0;
                color: #58a6ff;
                font-size: 18px;
                border-bottom: 1px solid var(--border-color);
                padding-bottom: 8px;
                text-align: center;
            }
            .card h3 {
                margin-top: 0;
                color: #58a6ff;
                font-size: 18px;
                border-bottom: 1px solid var(--border-color);
                padding-bottom: 8px;
            }
            .prices-row {
                display: flex;
                gap: 15px;
                margin-bottom: 15px;
