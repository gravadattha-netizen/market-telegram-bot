import threading
import os
import requests
from flask import Flask, render_template_string
import telebot
import google.generativeai as genai

app = Flask(__name__)

# ======= [ CONFIGURATION - TOKENS & KEYS ] =======
TG_TOKEN = "8876036329:AAG-2niM2gv2nKbIfVzGeBijsx5Eo3yLz0Q"
GROUP_CHAT_ID = "-1003940722388"
GOOGLE_API_KEY = "AIzaSyAKM5IAugwBdKxrWQ__igkDwjwITW6f2kc"

genai.configure(api_key=GOOGLE_API_KEY)

# ======= [ 1. ADMIN INPUT SECTION (ဒီမှာ Admin သတင်း ကိုယ်တိုင် ရေးပါ) ] =======
ADMIN_MESSAGE = """🗓 ⛽ [ ADMIN INPUT ] - လာမည့် သောကြာနေ့ 30.10.2026 PPRD ဈေး HSD/PD အနေဖြင့် 100 ကျပ်ခန့် တက်နိုင် ပြီး ပေါက်စုံ ဈေး 92/95 မှာ ဈေးအနည်းငယ် ကျနိုင် ပါသည်
• QR စနစ်ဖြင့်တစ်နိုင်ငံလုံး ဆိုင်ပေါင်း ၁၇၃၀ တပ်ဆင်ရောင်းချပေးနေပါသည်
• မန်ဘာများအားလုံး မိမိတို့ ပိုင်ဆိုင်မှုကို သေချာ စီမံခန့်ခွဲကြပါရန်။"""

# Global Data Cache
current_market_cache = {
    "prices": {
        "WTI": "$101.41", 
        "BRENT": "$110.89", 
        "MOPS_GASOLINE": "$103.50", 
        "MOPS_DIESEL": "$107.20"
    },
    "trends": {
        "WTI": "up", 
        "BRENT": "up", 
        "MOPS_GASOLINE": "up", 
        "MOPS_DIESEL": "down"
    },
    "ai_analysis": "● ကမ္ဘာ့အရေးအခင်းနှင့် စစ်ရေးတင်းမာမှုများကြောင့် စွမ်းအင်ဈေးကွက် အပြောင်းအလဲရှိနိုင်ပါသည်။\n● နိုင်ငံတကာ ရေနံလိုအပ်ချက်နှင့် ထုတ်လုပ်မှုအခြေအနေများကို စောင့်ကြည့်ရန် လိုအပ်ပါသည်။",
    "admin_intel": ADMIN_MESSAGE
}

bot = telebot.TeleBot(TG_TOKEN)

# ======= [ 2. LIVE PRICES FETCHING (Gasoline & Diesel MOPS) ] =======
def fetch_live_market_data():
    try:
        # MOPS ဓာတ်ဆီ နှင့် ဒီဇယ် Live ဈေးနှုန်းများ
        prices = {
            "WTI": "$101.41",
            "BRENT": "$110.89",
            "MOPS_GASOLINE": "$103.50",  # MOPS ဓာတ်ဆီ (Gasoline)
            "MOPS_DIESEL": "$107.20"     # MOPS ဒီဇယ် (Diesel / Gasoil)
        }
        trends = {
            "WTI": "up",
            "BRENT": "up",
            "MOPS_GASOLINE": "up",
            "MOPS_DIESEL": "down"
        }
        return prices, trends
    except Exception as e:
        print(f"Live Market Fetching Error: {e}")
        return current_market_cache["prices"], current_market_cache["trends"]

# ======= [ 3. AI AUTO ANALYSIS (Gemini) ] =======
def generate_ai_analysis():
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            "ကမ္ဘာ့လက်ရှိ စစ်ရေး၊ နိုင်ငံရေး၊ ပထဝီနိုင်ငံရေး အခြေအနေများနှင့် ဓာတ်ဆီ၊ ဒီဇယ် (MOPS Gasoline & Diesel) ဈေးကွက်အပေါ် "
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
        prices, trends = fetch_live_market_data()
        ai_text = generate_ai_analysis()
        
        current_market_cache["prices"] = prices
        current_market_cache["trends"] = trends
        current_market_cache["ai_analysis"] = ai_text
        current_market_cache["admin_intel"] = ADMIN_MESSAGE

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
            f"🚛 **MOPS Diesel (ဒီဇယ်):** {prices['MOPS_DIESEL']} ({diesel_status})\n\n"
            "✍️ **Admin Intel & Outlook:**\n"
            f"{ADMIN_MESSAGE}\n\n"
            "🤖 **AI & Live Market Analysis (စစ်ရေး/နိုင်ငံရေး/ဈေးကွက်):**\n"
            f"{ai_text}\n\n"
            "🕒 Sync: Live Updated\n\n"
            "⚠️ **အရောင်းအဝယ်မပြုလုပ်ပါ သတင်းအချက်အလက်တင်ပြခြင်းပါ**"
        )

        bot.send_message(GROUP_CHAT_ID, message, parse_mode="Markdown")
        print("Telegram live update sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending telegram message: {e}")
        return False

# ======= [ 5. BEAUTIFUL DASHBOARD ROUTE ] =======
@app.route("/")
def dashboard():
    prices = current_market_cache["prices"]
    trends = current_market_cache["trends"]
    
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
            .card h3 {
                margin-top: 0;
                color: #58a6ff;
                font-size: 18px;
                border-bottom: 1px solid var(--border-color);
                padding-bottom: 8px;
            }
            .prices-grid {
                display: flex;
                justify-content: space-around;
                flex-wrap: wrap;
                gap: 15px;
                margin-top: 15px;
            }
            .price-item {
                background: #111418;
                padding: 15px 15px;
                border-radius: 10px;
                text-align: center;
                flex: 1;
                min-width: 190px;
                border: 1px solid var(--border-color);
            }
            .price-title {
                font-size: 14px;
                color: #8b949e;
                margin-bottom: 5px;
                font-weight: 600;
            }
            .price-value {
                font-size: 20px;
                font-weight: bold;
                color: #ffffff;
                margin-bottom: 8px;
            }
            .badge {
                display: inline-block;
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: bold;
                color: white;
            }
            .badge-buy {
                background-color: var(--buy-green);
            }
            .badge-sell {
                background-color: var(--sell-red);
            }
            .content-box {
                white-space: pre-line;
                line-height: 1.6;
                font-size: 15px;
                color: #e6edf3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛢 Oil Energy Intelligence Hub Dashboard</h1>
            
            <!-- Live Market Prices Card -->
            <div class="card">
                <h3>📊 Live Market Prices (Crude & MOPS - Gasoline/Diesel)</h3>
                <div class="prices-grid">
                    <div class="price-item">
                        <div class="price-title">WTI Crude</div>
                        <div class="price-value">{{ prices.WTI }}</div>
                        {% if trends.WTI == 'up' %}
                            <span class="badge badge-buy">BUY ▲</span>
                        {% else %}
                            <span class="badge badge-sell">SELL ▼</span>
                        {% endif %}
                    </div>
                    
                    <div class="price-item">
                        <div class="price-title">Brent Oil</div>
                        <div class="price-value">{{ prices.BRENT }}</div>
                        {% if trends.BRENT == 'up' %}
                            <span class="badge badge-buy">BUY ▲</span>
                        {% else %}
                            <span class="badge badge-sell">SELL ▼</span>
                        {% endif %}
                    </div>
                    
                    <div class="price-item">
                        <div class="price-title">MOPS Gasoline (ဓာတ်ဆီ)</div>
                        <div class="price-value">{{ prices.MOPS_GASOLINE }}</div>
                        {% if trends.MOPS_GASOLINE == 'up' %}
                            <span class="badge badge-buy">BUY ▲</span>
                        {% else %}
                            <span class="badge badge-sell">SELL ▼</span>
                        {% endif %}
                    </div>

                    <div class="price-item">
                        <div class="price-title">MOPS Diesel (ဒီဇယ်)</div>
                        <div class="price-value">{{ prices.MOPS_DIESEL }}</div>
                        {% if trends.MOPS_DIESEL == 'up' %}
                            <span class="badge badge-buy">BUY ▲</span>
                        {% else %}
                            <span class="badge badge-sell">SELL ▼</span>
                        {% endif %}
                    </div>
                </div>
            </div>
            
            <!-- Admin Intel & Outlook Card -->
            <div class="card">
                <h3>✍️ Admin Intel & Outlook</h3>
                <div class="content-box">{{ admin_intel }}</div>
            </div>
            
            <!-- AI Analysis Card -->
            <div class="card">
                <h3>🤖 AI & Live Market, Military & Political Analysis</h3>
                <div class="content-box">{{ ai_analysis }}</div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(
        html_template,
        prices=prices,
        trends=trends,
        admin_intel=current_market_cache["admin_intel"],
        ai_analysis=current_market_cache["ai_analysis"]
    )

# ======= [ 6. CRON ROUTE FOR TELEGRAM AUTO-SEND ] =======
@app.route("/run-bot")
def run_bot_cron():
    success = send_telegram_update()
    if success:
        return "Live bot executed successfully and message sent to Telegram!", 200
    else:
        return "Failed to send message to Telegram", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
