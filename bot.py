import time
import requests
import threading
import os
import re
import xml.etree.ElementTree as ET
from flask import Flask, render_template_string
import telebot
import google.generativeai as genai

app = Flask('')

# ======= [ CONFIGURATION - TOKENS & KEYS ] =======
TG_TOKEN = "8646909789:AAFhLamWEWkqjnCd2pfjEXn5lMoBWPCejNo" 
GROUP_CHAT_ID = -1003940722388  
GOOGLE_API_KEY = "AIzaSyAKM5IAugwBdKxrWQ__igkDwjwITW6f2kc"

# Google Gemini API Configuration
genai.configure(api_key=GOOGLE_API_KEY)

# Global Data Storage Database Cache
current_market_cache = {
    "prices": {"BTC": 0.0, "ETH": 0.0, "GOLD": 0.0, "WTI": 0.0, "BRENT": 0.0, "DXY": 0.0},
    "display_prices": {"BTC": "$0.00", "ETH": "$0.00", "GOLD": "$0.00", "WTI": "$0.00", "BRENT": "$0.00", "DXY": "0.00"},
    "trends": {"BTC": "neutral", "ETH": "neutral", "GOLD": "neutral", "WTI": "neutral", "BRENT": "neutral", "DXY": "neutral"},
    "fng": "50 Neutral",
    "last_update": "N/A",
    "crypto_gauge": 50,
    "wti_gauge": 50,
    "brent_gauge": 50,
    "gold_gauge": 50,
    "ai_news": "စနစ်သစ်မှ ကမ္ဘာ့သတင်းများကို စုစည်း၍ AI Analysis ပြုလုပ်နေပါသည်...",
    
    # MOPS Tracker Data Storage
    "last_mops_text": "No custom MOPS news forwarded from group yet. Waiting for member updates...",
    "last_mops_user": "System",
    "last_mops_time": "N/A",
    "mops_trend": "neutral",
    "prev_mops_val": 0.0
}

# ======= [ HTML + DYNAMIC COLOR-CODED TWIN LAYOUT ] =======
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
        
        /* Twin Grid Layout */
        .twin-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 12px; }
        @media (max-width: 768px) { .twin-grid { grid-template-columns: 1fr; } }
        
        .twin-card { background: #0f172a; border-radius: 10px; border: 1px solid #1e293b; padding: 12px; }
        .twin-title { font-size: 0.8rem; color: #94a3b8; font-weight: bold; text-transform: uppercase; margin-bottom: 8px; border-bottom: 1px solid #1e293b; padding-bottom: 4px; }
        .twin-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #1e293b; }
        .twin-row:last-child { border-bottom: none; }
        .twin-label { font-size: 0.85rem; font-weight: 600; color: #cbd5e1; }
        .twin-val { font-size: 0.95rem; font-weight: 700; display: flex; align-items: center; gap: 4px; }

        /* Dynamic Visual Indicators colors */
        .color-up { color: #10b981 !important; }    
        .color-down { color: #ef4444 !important; }  
        .color-stable { color: #e2e8f0 !important; }

        /* Gauges Strip */
        .gauges-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 12px; }
        @media (max-width: 600px) { .gauges-grid { grid-template-columns: repeat(2, 1fr); } }
        .gauge-panel { background: #0f172a; border-radius: 10px; padding: 8px; border: 1px solid #1e293b; text-align: center; }
        .gauge-title { font-size: 0.7rem; color: #94a3b8; font-weight: 600; margin-bottom: 4px; }

        /* Lower Content Grid Panels */
        .news-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px; }
        @media (max-width: 768px) { .news-grid { grid-template-columns: 1fr; } }
        
        .news-box { background: #0f172a; border-radius: 10px; border: 1px solid #1e293b; padding: 12px; min-height: 220px; display: flex; flex-direction: column; }
        .news-header { font-size: 0.85rem; font-weight: bold; padding-bottom: 6px; margin-bottom: 8px; border-bottom: 1px solid #334155; }
        .news-content { font-size: 0.85rem; color: #cbd5e1; line-height: 1.6; white-space: pre-line; flex-grow: 1; overflow-y: auto; }
        
        .mops-container { background: #111827; border: 1px dashed #334155; padding: 10px; border-radius: 8px; margin-top: 4px; }
        .trend-badge { font-size: 0.85rem; font-weight: bold; display: inline-flex; align-items: center; gap: 4px; margin-bottom: 6px; padding: 4px 10px; border-radius: 6px; }
        .trend-up { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }
        .trend-down { background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }
        .trend-neutral { background: rgba(148, 163, 184, 0.15); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.3); }
        .mops-meta { font-size: 0.65rem; color: #64748b; text-align: right; margin-top: 8px; border-top: 1px solid #1e293b; padding-top: 4px; }

        footer { text-align: center; color: #ef4444; font-size: 0.8rem; font-weight: bold; padding: 10px; background: #111827; border-radius: 8px; border: 1px solid #1e293b; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div><h1>KYAW GYI INTELLIGENCE HUB ⚡ <span style="font-size:0.85rem; color:#facc15; font-weight:bold;">(မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ)</span></h1></div>
            <div class="sync-time">Last Sync: {{ data.last_update }}</div>
        </header>

        <div class="twin-grid">
            <div class="twin-card">
                <div class="twin-title">🪙 Markets & Currency Index</div>
                <div class="twin-row">
                    <span class="twin-label">Bitcoin (BTC)</span>
                    <span class="twin-val {% if data.trends.BTC == 'up' %}color-up{% elif data.trends.BTC == 'down' %}color-down{% else %}color-stable{% endif %}">
                        {{ data.display_prices.BTC }} {% if data.trends.BTC == 'up' %}▲{% elif data.trends.BTC == 'down' %}▼{% endif %}
                    </span>
                </div>
                <div class="twin-row">
                    <span class="twin-label">Ethereum (ETH)</span>
                    <span class="twin-val {% if data.trends.ETH == 'up' %}color-up{% elif data.trends.ETH == 'down' %}color-down{% else %}color-stable{% endif %}">
                        {{ data.display_prices.ETH }} {% if data.trends.ETH == 'up' %}▲{% elif data.trends.ETH == 'down' %}▼{% endif %}
                    </span>
                </div>
                <div class="twin-row">
                    <span class="twin-label">US Dollar Index (DXY)</span>
                    <span class="twin-val {% if data.trends.DXY == 'up' %}color-up{% elif data.trends.DXY == 'down' %}color-down{% else %}color-stable{% endif %}">
                        {{ data.display_prices.DXY }} {% if data.trends.DXY == 'up' %}▲{% elif data.trends.DXY == 'down' %}▼{% endif %}
                    </span>
                </div>
            </div>

            <div class="twin-card">
                <div class="twin-title">🛢 Energies & Spot Gold</div>
                <div class="twin-row">
                    <span class="twin-label">WTI Crude Oil</span>
                    <span class="twin-val {% if data.trends.WTI == 'up' %}color-up{% elif data.trends.WTI == 'down' %}color-down{% else %}color-stable{% endif %}">
                        {{ data.display_prices.WTI }} {% if data.trends.WTI == 'up' %}▲{% elif data.trends.WTI == 'down' %}▼{% endif %}
                    </span>
                </div>
                <div class="twin-row">
                    <span class="twin-label">Brent Crude Oil</span>
                    <span class="twin-val {% if data.trends.BRENT == 'up' %}color-up{% elif data.trends.BRENT == 'down' %}color-down{% else %}color-stable{% endif %}">
                        {{ data.display_prices.BRENT }} {% if data.trends.BRENT == 'up' %}▲{% elif data.trends.BRENT == 'down' %}▼{% endif %}
                    </span>
                </div>
                <div class="twin-row">
                    <span class="twin-label">Spot Gold (XAU/USD)</span>
                    <span class="twin-val {% if data.trends.GOLD == 'up' %}color-up{% elif data.trends.GOLD == 'down' %}color-down{% else %}color-stable{% endif %}">
                        {{ data.display_prices.GOLD }} {% if data.trends.GOLD == 'up' %}▲{% elif data.trends.GOLD == 'down' %}▼{% endif %}
                    </span>
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
                <div class="news-header" style="color: #60a5fa;">🤖 GOOD AI AUTOMATED MARKET ANALYSIS (မြန်မာလိုအနှစ်ချုပ်)</div>
                <div class="news-content">{{ data.ai_news }}</div>
            </div>

            <div class="news-box">
                <div class="news-header" style="color: #34d399;">📢 MEMBER DAILY MOPS TRACKER</div>
                <div class="news-content">
                    {% if data.last_mops_time != 'N/A' %}
                        {% if data.mops_trend == 'up' %}
                            <div class="trend-badge trend-up">▲ Singapore Prices Up (စိမ်း)</div>
                        {% elif data.mops_trend == 'down' %}
                            <div class="trend-badge trend-down">▼ Singapore Prices Down (နီ)</div>
                        {% else %}
                            <div class="trend-badge trend-neutral">■ Prices Stable / First Signal</div>
                        {% endif %}
                    {% endif %}
                    <div class="mops-container">
                        <div style="font-size:0.8rem; color:#cbd5e1; line-height:1.6; white-space: pre-line;">{{ data.last_mops_text }}</div>
                        <div class="mops-meta">Updated by {{ data.last_mops_user }} at {{ data.last_mops_time }}</div>
                    </div>
                </div>
            </div>
        </div>

        <footer>
            ⚠️ အရောင်းအဝယ်မပြုလုပ်ပါ သတင်းအချက်အလက်တင်ပြခြင်းပါ
        </footer>
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

# ======= [ EXTRACTION: DYNAMIC GLOBAL NEWS WIRE FEED ] =======
def fetch_global_wire_headlines():
    headlines = []
    # High quality financial news RSS providers (Investing.com & CNBC Wire)
    rss_urls = [
        "https://www.investing.com/rss/news_287.rss",  # Commodities/Gold/Oil news
        "https://www.investing.com/rss/crypto.rss"     # Crypto news feed
    ]
    for url in rss_urls:
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
            root = ET.fromstring(response.content)
            for item in root.findall('.//item')[:4]: # Pull top 4 critical reports smoothly
                title = item.find('title').text
                desc = item.find('description').text if item.find('description') is not None else ""
                headlines.append(f"- {title}: {desc[:110]}...")
        except:
            pass
    return "\n".join(headlines) if headlines else "No raw wire text compiled this cycle."

# ======= [ ADVANCED AI SYSTEM ANALYTICS ENGINE ] =======
def generate_ai_market_intelligence(prices, wire_raw_text):
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        prompt = (
            f"တရားဝင် စီးပွားရေးသတင်းထောက်တစ်ဦးကဲ့သို့ ပြုလုပ်ပါ။ အောက်ပါ ကမ္ဘာ့ဈေးနှုန်းများနှင့် သတင်းအချက်အလက်များကို အခြေခံ၍ "
            f"မြန်မာဘာသာဖြင့် သပ်ရပ်သန့်ရှင်းသော Bullet points ၄ ခုဖြင့် အဓိကစျေးကွက်သုံးသပ်ချက်ကို အနှစ်ချုပ်ရေးသားပေးပါ။\n\n"
            f"[လက်ရှိစျေးနှုန်းများ]:\n- Bitcoin (BTC): ${prices['BTC']}\n- Spot Gold (ရွှေ): ${prices['GOLD']}\n"
            f"- WTI Oil (ရေနံ): ${prices['WTI']}\n- US Dollar Index (DXY): {prices['DXY']}\n\n"
            f"[ကမ္ဘာ့သတင်းအချက်အလက်များ]:\n{wire_raw_text}\n\n"
            f"သတ်မှတ်ချက်: စာသားများကို ဖတ်ရလွယ်ကူအောင် ရှင်းလင်းစွာ အနှစ်ချုပ်ပါ။ အပိုစာသားများမထည့်ပါနှင့်။ စုစုပေါင်း စာလုံးရေ ၁၅၀ ထက်မပိုစေရ။"
        )
        response = model.generate_content(prompt)
        return response.text if response.text else "စျေးကွက်သတင်းများကို ပုံမှန်အတိုင်း စောင့်ကြည့်လေ့လာနေပါသည်။"
    except Exception as e:
        return f"⚠️ Good AI System Feed Notice: တိုက်ရိုက်သတင်းခွဲခြမ်းစိတ်ဖြာမှု ယာယီစင့်ခ်လုပ်နေဆဲဖြစ်ပါသည်။"

# ======= [ TELEGRAM DATA REPORT ENGINE ] =======
def generate_report_text():
    disp = current_market_cache["display_prices"]
    trends = current_market_cache["trends"]
    fng = current_market_cache["fng"]
    ai_report = current_market_cache["ai_news"]
    
    def get_arrow(asset_key):
        if trends[asset_key] == "up": return "▲ (တက်)"
        elif trends[asset_key] == "down": return "▼ (ကျ)"
        return "■"

    mops_trend_status = ""
    if current_market_cache["last_mops_time"] != "N/A":
        if current_market_cache["mops_trend"] == "up":
            mops_trend_status = "\n📈 **MOPS Trend:** Singapore Prices Up (စိမ်း) ▲"
        elif current_market_cache["mops_trend"] == "down":
            mops_trend_status = "\n📉 **MOPS Trend:** Singapore Prices Down (နီ) ▼"

    return (
        "✨ 🟡 **(မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ)** 🟡 ✨\n\n"
        "📊 **Market Intelligence Update**\n\n"
        f"🪙 **BTC:** {disp['BTC']} {get_arrow('BTC')} | **ETH:** {disp['ETH']} {get_arrow('ETH')}\n"
        f"🛢 **WTI:** {disp['WTI']} {get_arrow('WTI')} | **BRENT:** {disp['BRENT']} {get_arrow('BRENT')}\n"
        f"🟡 **GOLD:** {disp['GOLD']} {get_arrow('GOLD')} | 💵 **DXY:** {disp['DXY']} {get_arrow('DXY')}\n"
        f"{mops_trend_status}\n\n"
        f"📈 **Crypto Fear & Greed:** {fng}\n"
        f"🕒 **Last Sync:** {current_market_cache['last_update']}\n\n"
        f"🤖 **Good AI Market Analysis (မြန်မာလို):**\n{ai_report}\n\n"
        "⚠️ **အရောင်းအဝယ်မပြုလုပ်ပါ သတင်းအချက်အလက်တင်ပြခြင်းပါ**"
    )

# ======= [ INBOUND TELEGRAM MESSAGES CONTROLLER ] =======
@bot.message_handler(func=lambda message: True)
def handle_group_messages(message):
    user_text = message.text
    if not user_text:
        return

    mops_keywords = ["mops", "singapore", "10ppm", "92r", "95r", "97r", "စက်သုံးဆီ", "ဆီဈေး"]
    if any(kw in user_text.lower() for kw in mops_keywords):
        sender_name = message.from_user.first_name or "Member"
        numbers = [float(n) for n in re.findall(r"\d+\.\d+|\d+", user_text)]
        current_val = sum(numbers) / len(numbers) if numbers else 0.0
        
        prev_val = current_market_cache["prev_mops_val"]
        if prev_val > 0.0 and current_val > 0.0:
            if current_val > prev_val:
                current_market_cache["mops_trend"] = "up"
            elif current_val < prev_val:
                current_market_cache["mops_trend"] = "down"
        
        if current_val > 0.0:
            current_market_cache["prev_mops_val"] = current_val

        current_market_cache["last_mops_text"] = user_text
        current_market_cache["last_mops_user"] = sender_name
        current_market_cache["last_mops_time"] = time.strftime("%I:%M %p")

    cmd_keywords = ["price", "ဈေး", "/price", "သတင်း", "breaking", "news", "brent", "wti", "dxy"]
    if any(kw in user_text.lower() for kw in cmd_keywords):
        try:
            bot.reply_to(message, generate_report_text())
        except Exception as e:
            print(f"Command processing error: {e}")

# ======= [ LIVE FINANCIAL TICKERS EXTRACTION ] =======
def get_market_data():
    prices = {"BTC": 0.0, "ETH": 0.0, "GOLD": 0.0, "WTI": 0.0, "BRENT": 0.0, "DXY": 0.0}
    disp = {"BTC": "0", "ETH": "0", "GOLD": "0", "WTI": "0", "BRENT": "0", "DXY": "0"}
    headers = {"User-Agent": "Mozilla/5.0"}
    timestamp = int(time.time())
    
    try:
        crypto_url = f"https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,PAXG&tsyms=USD&_cb={timestamp}"
        res = requests.get(crypto_url, headers=headers, timeout=12).json()
        if "BTC" in res:
            prices["BTC"] = float(res['BTC']['USD'])
            prices["ETH"] = float(res['ETH']['USD'])
            prices["GOLD"] = float(res['PAXG']['USD'])
            for k in ["BTC", "ETH", "GOLD"]:
                disp[k] = f"${prices[k]:,.2f}"
    except: pass

    try:
        oil_url = f"https://query1.finance.yahoo.com/v8/finance/chart/CL=F?interval=1d&range=1d&_cb={timestamp}"
        wti_res = requests.get(oil_url, headers=headers, timeout=10).json()
        prices["WTI"] = float(wti_res['chart']['result'][0]['meta']['regularMarketPrice'])
        disp["WTI"] = f"${prices['WTI']:,.2f}"
    except: pass

    try:
        oil_url2 = f"https://query1.finance.yahoo.com/v8/finance/chart/BZ=F?interval=1d&range=1d&_cb={timestamp}"
        bt_res = requests.get(oil_url2, headers=headers, timeout=10).json()
        prices["BRENT"] = float(bt_res['chart']['result'][0]['meta']['regularMarketPrice'])
        disp["BRENT"] = f"${prices['BRENT']:,.2f}"
    except: pass

    try:
        dxy_url = f"https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB?interval=1d&range=1d&_cb={timestamp}"
        dxy_res = requests.get(dxy_url, headers=headers, timeout=10).json()
        prices["DXY"] = float(dxy_res['chart']['result'][0]['meta']['regularMarketPrice'])
        disp["DXY"] = f"{prices['DXY']:,.2f}"
    except: pass

    return prices, disp

def get_fng_value():
    try:
        res = requests.get("https://api.alternative.me/fng/").json()
        val = int(res['data'][0]['value'])
        lbl = res['data'][0]['value_classification']
        return val, f"{val} {lbl}"
    except: return 50, "50 Neutral"

def update_all():
    old_prices = current_market_cache["prices"].copy()
    prices, disp = get_market_data()
    fng_val, fng_lbl = get_fng_value()
    
    for asset in prices:
        if old_prices[asset] > 0.0 and prices[asset] > 0.0:
            if prices[asset] > old_prices[asset]:
                current_market_cache["trends"][asset] = "up"
            elif prices[asset] < old_prices[asset]:
                current_market_cache["trends"][asset] = "down"
    
    current_market_cache["crypto_gauge"] = fng_val
    current_market_cache["wti_gauge"] = 45 if prices["WTI"] < 82 else 75
    current_market_cache["brent_gauge"] = 45 if prices["BRENT"] < 85 else 75
    current_market_cache["gold_gauge"] = 80
    
    current_market_cache["prices"] = prices
    current_market_cache["display_prices"] = disp
    current_market_cache["fng"] = fng_lbl
    current_market_cache["last_update"] = time.strftime("%I:%M %p")
    
    # SYSTEM CRITICAL PIPELINE: Fetch headlines -> AI Summarization Engine
    wire_raw_text = fetch_global_wire_headlines()
    current_market_cache["ai_news"] = generate_ai_market_intelligence(prices, wire_raw_text)

# ======= [ THE 4-HOUR CRON PRODUCTION WORKER ] =======
def auto_worker():
    update_all()
    try:
        bot.send_message(GROUP_CHAT_ID, generate_report_text())
    except Exception as e:
        print(f"Initial worker dispatch sequence fault: {e}")

    while True:
        time.sleep(14400) # Wait 4-Hours precisely to minimize API token wear
        update_all()
        try:
            bot.send_message(GROUP_CHAT_ID, generate_report_text())
        except Exception as e:
            print(f"Auto-worker periodic loop fail: {e}")

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
