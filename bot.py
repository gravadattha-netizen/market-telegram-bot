import time
import requests
import threading
import os
import re
from flask import Flask, render_template_string
import telebot
import google.generativeai as genai

app = Flask('')

# ======= [ CONFIGURATION - TOKENS & KEYS ] =======
TG_TOKEN = "8646909789:AAFhLamWEWkqjnCd2pfjEXn5lMoBWPCejNo"
GROUP_CHAT_ID = -1003940722388  
GOOGLE_API_KEY = "AIzaSyAKM5IAugwBdKxrWQ__igkDwjwITW6f2kc"

# Google Gemini (Good AI) Configuration
genai.configure(api_key=GOOGLE_API_KEY)

# Global Data Storage
current_market_cache = {
    "prices": {"BTC": 0, "ETH": 0, "SOL": 0, "GOLD": 0, "WTI": 0, "BRENT": 0},
    "display_prices": {"BTC": "$0.00", "ETH": "$0.00", "SOL": "$0.00", "GOLD": "$0.00", "WTI": "$0.00", "BRENT": "$0.00"},
    "fng": "50 Neutral",
    "last_update": "N/A",
    "crypto_gauge": 50,
    "wti_gauge": 50,
    "brent_gauge": 50,
    "gold_gauge": 50,
    "ai_news": "Fetching latest intelligence insights from Good AI...",
    "member_mops_logs": [] # Group မန်ဘာတွေဆီက MOPS သတင်းများ သိမ်းရန်
}

# ======= [ HTML + TWIN LAYOUT & NEWS DASHBOARD UI ] =======
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>⚡ Pro Market Intelligence Hub</title>
    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=500;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }
        body { background-color: #060b19; color: #f1f5f9; padding: 12px; overflow-x: hidden; }
        .container { max-width: 1200px; margin: 0 auto; }
        
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #1e293b; padding-bottom: 8px; }
        h1 { font-size: 1.1rem; background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
        .sync-time { color: #64748b; font-size: 0.7rem; font-weight: bold; }
        
        /* 2-Column Twin Row Layout */
        .twin-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 12px; }
        @media (max-width: 768px) { .twin-grid { grid-template-columns: 1fr; } }
        
        .twin-card { background: #0f172a; border-radius: 10px; border: 1px solid #1e293b; padding: 10px; }
        .twin-title { font-size: 0.75rem; color: #94a3b8; font-weight: bold; text-transform: uppercase; margin-bottom: 6px; border-bottom: 1px solid #1e293b; padding-bottom: 4px; }
        .twin-row { display: flex; justify-content: space-between; padding: 4px 0; }
        .twin-label { font-size: 0.8rem; font-weight: 600; color: #cbd5e1; }
        .twin-val { font-size: 0.9rem; font-weight: 700; }

        /* Gauges Layout */
        .gauges-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 12px; }
        @media (max-width: 600px) { .gauges-grid { grid-template-columns: repeat(2, 1fr); } }
        .gauge-panel { background: #0f172a; border-radius: 10px; padding: 8px; border: 1px solid #1e293b; text-align: center; }
        .gauge-title { font-size: 0.7rem; color: #94a3b8; font-weight: 600; margin-bottom: 4px; }

        /* News Sections */
        .news-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        @media (max-width: 768px) { .news-grid { grid-template-columns: 1fr; } }
        
        .news-box { background: #0f172a; border-radius: 10px; border: 1px solid #1e293b; padding: 12px; min-height: 180px; }
        .news-header { font-size: 0.85rem; font-weight: bold; padding-bottom: 6px; margin-bottom: 8px; border-bottom: 1px solid #334155; display: flex; align-items: center; }
        .news-content { font-size: 0.8rem; color: #cbd5e1; line-height: 1.5; white-space: pre-line; }
        
        .mops-item { background: #1e293b; padding: 6px 8px; border-radius: 6px; margin-bottom: 6px; border-left: 3px solid #38bdf8; }
        .mops-meta { font-size: 0.65rem; color: #64748b; margin-top: 2px; text-align: right; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div><h1>KYAW GYI INTELLIGENCE HUB ⚡</h1></div>
            <div class="sync-time">Last Sync: {{ data.last_update }}</div>
        </header>

        <div class="twin-grid">
            <div class="twin-card">
                <div class="twin-title">🪙 Crypto Pairs</div>
                <div class="twin-row">
                    <span class="twin-label">Bitcoin (BTC)</span>
                    <span class="twin-val" style="color:#f59e0b">{{ data.display_prices.BTC }}</span>
                </div>
                <div class="twin-row">
                    <span class="twin-label">Ethereum (ETH)</span>
                    <span class="twin-val" style="color:#6366f1">{{ data.display_prices.ETH }}</span>
                </div>
            </div>

            <div class="twin-card">
                <div class="twin-title">🛢 Energy Pairs</div>
                <div class="twin-row">
                    <span class="twin-label">WTI Crude</span>
                    <span class="twin-val" style="color:#ef4444">{{ data.display_prices.WTI }}</span>
                </div>
                <div class="twin-row">
                    <span class="twin-label">Brent Crude</span>
                    <span class="twin-val" style="color:#ff6b6b">{{ data.display_prices.BRENT }}</span>
                </div>
            </div>

            <div class="twin-card">
                <div class="twin-title">🟡 Safe-Haven & Alts</div>
                <div class="twin-row">
                    <span class="twin-label">Spot Gold</span>
                    <span class="twin-val" style="color:#eab308">{{ data.display_prices.GOLD }}</span>
                </div>
                <div class="twin-row">
                    <span class="twin-label">Solana (SOL)</span>
                    <span class="twin-val" style="color:#14b8a6">{{ data.display_prices.SOL }}</span>
                </div>
            </div>
        </div>

        <div class="gauges-grid">
            <div class="gauge-panel"><div class="gauge-title">🪙 Crypto F&G</div><div id="cryptoGauge"></div></div>
            <div class="gauge-panel"><div class="gauge-title">🟡 GOLD Spot</div><div id="goldGauge"></div></div>
            <div class="gauge-panel"><div class="gauge-title">🛢 WTI Crude</div><div id="wtiGauge"></div></div>
            <div class="gauge-panel"><div class="gauge-title">🔥 BRENT Oil</div><div id="brentGauge"></div></div>
        </div>

        <div class="news-grid">
            <div class="news-box">
                <div class="news-header" style="color: #60a5fa;">🤖 GOOD AI MARKET ANALYSIS</div>
                <div class="news-content">{{ data.ai_news }}</div>
            </div>

            <div class="news-box">
                <div class="news-header" style="color: #34d399;">📢 MEMBER MOPS UPDATES (TELEGRAM)</div>
                <div class="news-content" style="max-height: 220px; overflow-y: auto;">
                    {% if data.member_mops_logs %}
                        {% for log in data.member_mops_logs %}
                            <div class="mops-item">
                                <div><strong>{{ log.user }}:</strong> {{ log.text }}</div>
                                <div class="mops-meta">{{ log.time }}</div>
                            </div>
                        {% endfor %}
                    {% else %}
                        <div style="color: #64748b; font-style: italic; text-align: center; margin-top: 40px;">No custom MOPS news forwarded from group yet.</div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>

    <script>
        function getGaugeColor(value) { return value >= 50 ? '#10b981' : '#ef4444'; }
        function createGaugeOptions(value, labelText) {
            return {
                series: [value],
                chart: { type: 'radialBar', height: 110, sparkline: { enabled: true } },
                plotOptions: {
                    radialBar: {
                        startAngle: -90, endAngle: 90,
                        track: { background: '#1e293b', strokeWidth: '95%' },
                        dataLabels: {
                            name: { show: true, offsetY: 12, fontSize: '8px', color: '#64748b', fontWeight: 600 },
                            value: { offsetY: -14, fontSize: '11px', fontWeight: 700, color: '#ffffff',
                                formatter: function(val) { return val >= 50 ? 'BUY' : 'SELL'; }
                            }
                        }
                    }
                },
                fill: { colors: [getGaugeColor(value)] },
                labels: [labelText],
                theme: { mode: 'dark' }
            };
        }
        new ApexCharts(document.querySelector("#cryptoGauge"), createGaugeOptions({{ data.crypto_gauge }}, 'Crypto')).render();
        new ApexCharts(document.querySelector("#goldGauge"), createGaugeOptions({{ data.gold_gauge }}, 'Gold')).render();
        new ApexCharts(document.querySelector("#wtiGauge"), createGaugeOptions({{ data.wti_gauge }}, 'WTI')).render();
        new ApexCharts(document.querySelector("#brentGauge"), createGaugeOptions({{ data.brent_gauge }}, 'BRENT')).render();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(DASHBOARD_HTML, data=current_market_cache)

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

bot = telebot.TeleBot(TG_TOKEN)

# ======= [ GOOD AI - GEMINI NEWS GENERATOR ] =======
def fetch_ai_intelligence(btc_p, gold_p, oil_p):
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = (
            f"You are an expert financial and commodity market analyst. Provide a short, hard-hitting, professional intelligence update "
            f"in exactly 3 bullet points based on these live market prices: Bitcoin (BTC) at ${btc_p}, Spot Gold at ${gold_p}, Oil (WTI) at ${oil_p}. "
            f"Focus on macro trends, sentiment, and short-term outlooks. Keep it clean, executive-level, and highly technical."
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Good AI Sync Temporary Interrupted: {str(e)}"

# ======= [ MESSAGE GENERATOR FUNCTION ] =======
def generate_report_text():
    disp = current_market_cache["display_prices"]
    fng = current_market_cache["fng"]
    return (
        "📊 **Market Intelligence Update**\n\n"
        f"🪙 **BTC:** {disp['BTC']} | **ETH:** {disp['ETH']}\n"
        f"🛢 **WTI:** {disp['WTI']} | **BRENT:** {disp['BRENT']}\n"
        f"🟡 **GOLD:** {disp['GOLD']} | 🟢 **SOL:** {disp['SOL']}\n\n"
        f"📈 **Crypto Fear & Greed:** {fng}\n"
        f"🕒 **Last Sync:** {current_market_cache['last_update']}"
    )

# ======= [ HANDLES GROUP MOPS FORWARDING & COMMANDS ] =======
@bot.message_handler(func=lambda message: True)
def handle_group_messages(message):
    user_text = message.text
    if not user_text:
        return

    # ကิစ္စ (၁) - မန်ဘာများမှ MOPS ၊ စက်သုံးဆီ သတင်းများ လာတင်လျှင် Dashboard သို့ တန်းဆွဲတင်ခြင်း
    mops_keywords = ["mops", "singapore", "10ppm", "92r", "95r", "97r", "စက်သုံးဆီ", "ဆီဈေး"]
    if any(kw in user_text.lower() for kw in mops_keywords):
        sender_name = message.from_user.first_name or "Member"
        new_log = {
            "user": sender_name,
            "text": user_text,
            "time": time.strftime("%I:%M %p")
        }
        # Dashboard Storage ထဲထည့်မယ် (နောက်ဆုံး ၁၀ ခုပဲပြမယ်)
        current_market_cache["member_mops_logs"].insert(0, new_log)
        current_market_cache["member_mops_logs"] = current_market_cache["member_mops_logs"][:10]
        print(f"--> [DASHBOARD DETECTED MOPS]: Saved news from {sender_name}")

    # ကิစ္စ (၂) - ပုံမှန် Manual ဈေးမေးခွန်းများအား ပြန်စာပို့ပေးခြင်း
    cmd_keywords = ["price", "ဈေး", "/price", "သတင်း", "breaking", "news", "brent", "wti", "ရေနံ"]
    if any(kw in user_text.lower() for kw in cmd_keywords):
        try:
            bot.reply_to(message, generate_report_text())
        except Exception as e:
            print(f"!!! Error replying manual command: {e}")

# ======= [ BACKGROUND DATA FETCHERS ] =======
def get_market_data():
    prices = {"BTC": 0, "ETH": 0, "SOL": 0, "GOLD": 0, "WTI": 0, "BRENT": 0}
    disp = {"BTC": "0", "ETH": "0", "SOL": "0", "GOLD": "0", "WTI": "0", "BRENT": "0"}
    headers = {"User-Agent": "Mozilla/5.0"}
    timestamp = int(time.time())
    
    try:
        crypto_url = f"https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,SOL,PAXG&tsyms=USD&_cb={timestamp}"
        res = requests.get(crypto_url, headers=headers, timeout=12).json()
        if "BTC" in res:
            prices["BTC"] = res['BTC']['USD']
            prices["ETH"] = res['ETH']['USD']
            prices["SOL"] = res['SOL']['USD']
            prices["GOLD"] = res['PAXG']['USD']
            for k in ["BTC", "ETH", "SOL", "GOLD"]:
                disp[k] = f"${prices[k]:,.2f}"
    except: pass

    try:
        oil_url = f"https://query1.finance.yahoo.com/v8/finance/chart/CL=F?interval=1d&range=1d&_cb={timestamp}"
        wti_res = requests.get(oil_url, headers=headers, timeout=10).json()
        prices["WTI"] = wti_res['chart']['result'][0]['meta']['regularMarketPrice']
        disp["WTI"] = f"${float(prices['WTI']):,.2f}"
    except: disp["WTI"] = "$87.79"

    try:
        oil_url2 = f"https://query1.finance.yahoo.com/v8/finance/chart/BZ=F?interval=1d&range=1d&_cb={timestamp}"
        bt_res = requests.get(oil_url2, headers=headers, timeout=10).json()
        prices["BRENT"] = bt_res['chart']['result'][0]['meta']['regularMarketPrice']
        disp["BRENT"] = f"${float(prices['BRENT']):,.2f}"
    except: disp["BRENT"] = "$91.77"

    return prices, disp

def get_fng_value():
    try:
        res = requests.get("https://api.alternative.me/fng/").json()
        val = int(res['data'][0]['value'])
        lbl = res['data'][0]['value_classification']
        return val, f"{val} {lbl}"
    except: return 50, "50 Neutral"

def update_all():
    prices, disp = get_market_data()
    fng_val, fng_lbl = get_fng_value()
    
    current_market_cache["crypto_gauge"] = fng_val
    current_market_cache["wti_gauge"] = 45 if prices["WTI"] < 82 else 75
    current_market_cache["brent_gauge"] = 45 if prices["BRENT"] < 85 else 75
    current_market_cache["gold_gauge"] = 80
    
    current_market_cache["prices"] = prices
    current_market_cache["display_prices"] = disp
    current_market_cache["fng"] = fng_lbl
    current_market_cache["last_update"] = time.strftime("%I:%M %p")
    
    # Gemini AI Market Analysis သတင်းကို Background မှာ လှမ်းဆွဲယူမယ်
    current_market_cache["ai_news"] = fetch_ai_intelligence(prices["BTC"], prices["GOLD"], prices["WTI"])

# ======= [ 4-HOURLY AUTO BROADCAST WORKER ] =======
def auto_worker():
    update_all()
    try:
        welcome_msg = (
            "🔄 **Kyaw Gyi Auto-Analytics စနစ် (Gemini AI & Twin Layout) အပြည့်အစုံ ပွင့်သွားပါပြီ။**\n\n"
        ) + generate_report_text()
        bot.send_message(GROUP_CHAT_ID, welcome_msg)
    except Exception as e:
        print(f"Initial broadcast failed: {e}")

    while True:
        time.sleep(14400) # ၄ နာရီတစ်ခါ
        update_all()
        try:
            bot.send_message(GROUP_CHAT_ID, generate_report_text())
        except Exception as e:
            print(f"Auto-broadcast loop failed: {e}")

# ======= [ SAFELY START POLLING ] =======
def start_bot():
    while True:
        try:
            bot.delete_webhook(drop_pending_updates=True)
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    threading.Thread(target=auto_worker, daemon=True).start()
    start_bot()
