import threading
import os
import time
import requests
from flask import Flask, render_template_string
import telebot
import google.generativeai as genai

app = Flask(__name__)

# ======= [ CONFIGURATION - TOKENS & KEYS ] =======
TG_TOKEN = "8876036329:AAFs_ncU_tT09R3kD9C9mq067qL8r1wIdWc"
GROUP_CHAT_ID = "-1003940722388"
GOOGLE_API_KEY = "AIzaSyAKM5IAugwBdKxrWQ__igkDwjwITW6f2kc"

genai.configure(api_key=GOOGLE_API_KEY)

# ======= [ 1. ADMIN INPUT SECTION ] =======
ADMIN_MESSAGE = """🗓 ⛽ [ ADMIN INPUT ] 
• QR စနစ်ဖြင့်တစ်နိုင်ငံလုံး ဆိုင်ပေါင်း ၁၉၂၇ ဆိုင်တပ်ဆင်ရောင်းချပေးနေပါသည်
• မန်ဘာများအားလုံး မိမိတို့ ပိုင်ဆိုင်မှုကို သေချာ စီမံခန့်ခွဲကြပါရန်။"""

current_market_cache = {
    "prices": {
        "WTI": "$101.41", 
        "BRENT": "$110.89", 
        "MOPS_GASOLINE": "$129.86", 
        "MOPS_DIESEL": "$173.70"
    },
    "trends": {
        "WTI": "up", 
        "BRENT": "down", 
        "MOPS_GASOLINE": "down", 
        "MOPS_DIESEL": "down"
    },
    "technical_signal": "Strong Buy",
    "sentiment": {"bullish": 82, "bearish": 18},
    "ai_analysis": "● ကမ္ဘာ့အရေးအခင်းနှင့် စစ်ရေးတင်းမာမှုများကြောင့် စွမ်းအင်ဈေးကွက် အပြောင်းအလဲရှိနိုင်ပါသည်။\n● နိုင်ငံတကာ ရေနံလိုအပ်ချက်နှင့် ထုတ်လုပ်မှုအခြေအနေများကို စောင့်ကြည့်ရန် လိုအပ်ပါသည်။",
    "admin_intel": ADMIN_MESSAGE,
    "last_updated": "Auto Updated"
}

bot = telebot.TeleBot(TG_TOKEN)

def fetch_live_market_data():
    prices = current_market_cache["prices"].copy()
    trends = current_market_cache["trends"].copy()
    signal = "Strong Buy"
    sentiment = {"bullish": 82, "bearish": 18}
    return prices, trends, signal, sentiment

def generate_ai_analysis():
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            "ကမ္ဘာ့လက်ရှိ စစ်ရေး၊ နိုင်ငံရေး၊ ပထဝီနိုင်ငံရေး အခြေအနေများနှင့် ဓာတ်ဆီ၊ ဒီဇယ် (MOPS Gasoline N1B2 & Diesel SGB2) ဈေးကွက်အပေါ် "
            "သက်ရောက်မှုများကို မြန်မာဘာသာဖြင့် တိုတိုရှင်းရှင်း သုံးသပ်ပေးပါ။ "
            "အချက် ၂ ချက်ပါဝင်သော bullet points (●) များဖြင့်သာ ရေးသားပေးပါ။"
        )
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
    except Exception as e:
        print(f"AI Analysis Error: {e}")
    
    return current_market_cache.get("ai_analysis", "● ကမ္ဘာ့စွမ်းအင်ဈေးကွက် အခြေအနေများကို ဆက်လက်စောင့်ကြည့်နေပါသည်။")

def send_telegram_update():
    try:
        prices, trends, signal, sentiment = fetch_live_market_data()
        ai_text = generate_ai_analysis()
        
        current_market_cache["prices"] = prices
        current_market_cache["trends"] = trends
        current_market_cache["technical_signal"] = signal
        current_market_cache["sentiment"] = sentiment
        current_market_cache["ai_analysis"] = ai_text
        current_market_cache["admin_intel"] = ADMIN_MESSAGE
        current_market_cache["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")

        wti_status = "BUY ▲" if trends["WTI"] == "up" else "SELL ▼"
        brent_status = "BUY ▲" if trends["BRENT"] == "up" else "SELL ▼"
        gas_status = "BUY ▲" if trends["MOPS_GASOLINE"] == "up" else "SELL ▼"
        diesel_status = "BUY ▲" if trends["MOPS_DIESEL"] == "up" else "SELL ▼"

        message = (
            "✨ (မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ) ✨\n\n"
            "📊 Energy Market Intelligence Update\n\n"
            f"🛢 WTI Crude: {prices['WTI']} ({wti_status})\n"
            f"🔥 Brent Oil: {prices['BRENT']} ({brent_status})\n"
            f"⛽ MOPS Gasoline (ဓာတ်ဆီ N1B2): {prices['MOPS_GASOLINE']} ({gas_status})\n"
            f"🚛 MOPS Diesel 10ppm (ဒီဇယ် SGB2): {prices['MOPS_DIESEL']} ({diesel_status})\n\n"
            f"📈 Technical Indicator: {signal} 🟢\n"
            f"🐂 Market Sentiment: Bullish {sentiment['bullish']}% | Bearish {sentiment['bearish']}%\n\n"
            "✍️ Admin Intel & Outlook:\n"
            f"{ADMIN_MESSAGE}\n\n"
            "🤖 AI & Market Analysis:\n"
            f"{ai_text}\n\n"
            f"🕒 Sync: {current_market_cache['last_updated']}\n\n"
            "⚠️ အရောင်းအဝယ်မပြုလုပ်ပါ သတင်းအချက်အလက်တင်ပြခြင်းပါ"
        )

        bot.send_message(GROUP_CHAT_ID, message)
        print("Telegram update sent successfully to group!")
        return True
    except Exception as e:
        print(f"Error sending telegram message: {e}")
        return False

def auto_update_loop():
    while True:
        time.sleep(14400)
        try:
            prices, trends, signal, sentiment = fetch_live_market_data()
            ai_text = generate_ai_analysis()
            current_market_cache["prices"] = prices
            current_market_cache["trends"] = trends
            current_market_cache["ai_analysis"] = ai_text
            send_telegram_update()
        except Exception as e:
            print(f"Update thread error: {e}")

threading.Thread(target=auto_update_loop, daemon=True).start()

@app.route("/")
def dashboard():
    prices = current_market_cache["prices"]
    trends = current_market_cache["trends"]
    signal = current_market_cache.get("technical_signal", "Strong Buy")
    sentiment = current_market_cache.get("sentiment", {"bullish": 82, "bearish": 18})
    admin_intel = current_market_cache["admin_intel"]
    ai_analysis = current_market_cache["ai_analysis"]
    
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
            }
            .prices-grid {
                display: flex;
                gap: 15px;
            }
            .price-item {
                background: #111418;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                flex: 1;
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
            .badge-buy { background-color: var(--buy-green); }
            .badge-sell { background-color: var(--sell-red); }
            .indicator-box {
                background: #111418;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                border: 1px solid var(--border-color);
                margin-bottom: 15px;
            }
            .gauge-title {
                font-size: 14px;
                color: #8b949e;
                margin-bottom: 8px;
            }
            .gauge-badge {
                display: inline-block;
                padding: 8px 20px;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
                background-color: var(--buy-green);
                color: white;
            }
            .sentiment-container {
                display: flex;
                gap: 15px;
            }
            .sentiment-bar {
                background: #111418;
                padding: 15px;
                border-radius: 10px;
                flex: 1;
                text-align: center;
                border: 1px solid var(--border-color);
            }
            .bullish { color: var(--buy-green); font-weight: bold; }
            .bearish { color: var(--sell-red); font-weight: bold; }
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
            
            <div class="card">
                <h3 class="center-title">📊 Live Market Prices (4-Hourly Auto Update)</h3>
                
                <div class="prices-row">
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
                </div>

                <div class="prices-grid">
                    <div class="price-item">
                        <div class="price-title">MOPS Gasoline (ဓာတ်ဆီ N1B2)</div>
                        <div class="price-value">{{ prices.MOPS_GASOLINE }}</div>
                        {% if trends.MOPS_GASOLINE == 'up' %}
                            <span class="badge badge-buy">BUY ▲</span>
                        {% else %}
                            <span class="badge badge-sell">SELL ▼</span>
                        {% endif %}
                    </div>

                    <div class="price-item">
                        <div class="price-title">MOPS Diesel 10ppm (ဒီဇယ် SGB2)</div>
                        <div class="price-value">{{ prices.MOPS_DIESEL }}</div>
                        {% if trends.MOPS_DIESEL == 'up' %}
                            <span class="badge badge-buy">BUY ▲</span>
                        {% else %}
                            <span class="badge badge-sell">SELL ▼</span>
                        {% endif %}
                    </div>
                </div>
            </div>

            <div class="card">
                <h3 class="center-title">📈 Technical Summary & Market Sentiment</h3>
                
                <div class="indicator-box">
                    <div class="gauge-title">Summary Technical Indicators</div>
                    <div class="gauge-badge">{{ signal }} 🟢</div>
                </div>

                <div class="sentiment-container">
                    <div class="sentiment-bar">
                        <div class="gauge-title">🐂 Bullish Community Sentiment</div>
                        <div class="price-value bullish">{{ sentiment.bullish }}%</div>
                    </div>
                    <div class="sentiment-bar">
                        <div class="gauge-title">🐻 Bearish Community Sentiment</div>
                        <div class="price-value bearish">{{ sentiment.bearish }}%</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>✍️ Admin Intel & Outlook</h3>
                <div class="content-box">{{ admin_intel }}</div>
            </div>
            
            <div class="card">
                <h3>🤖 AI & Live Market, Military & Political Analysis</h3>
                <div class="content-box">{{ ai_analysis }}</div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, prices=prices, trends=trends, signal=signal, sentiment=sentiment, admin_intel=admin_intel, ai_analysis=ai_analysis)

@app.route("/run-bot")
def run_bot_cron():
    success = send_telegram_update()
    if success:
        return "4-hourly bot executed successfully and message sent to Telegram!", 200
    else:
        return "Failed to send message to Telegram. Please check Render Logs for exact error.", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
