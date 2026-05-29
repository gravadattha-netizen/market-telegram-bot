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

genai.configure(api_key=GOOGLE_API_KEY)

# Global Data Cache
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
    "ai_news": "ကမ္ဘာ့စီးပွားရေးသတင်းများကို AI ဖြင့် အနှစ်ချုပ် သုံးသပ်နေပါသည်...",
    "last_mops_text": "မန်ဘာများမှ MOPS သတင်း လာတင်သည်ကို စောင့်ဆိုင်းနေပါသည်...",
    "last_mops_user": "System",
    "last_mops_time": "N/A",
    "mops_trend": "neutral",
    "prev_mops_val": 0.0
}

# ======= [ HTML UI - DESIGN FIXED ] =======
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ Kyaw Gyi Market Intelligence Hub</title>
    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }
        body { background-color: #060b19; color: #f1f5f9; padding: 15px; overflow-x: hidden; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 2px solid #1e293b; padding-bottom: 10px; }
        h1 { font-size: 1.2rem; color: #38bdf8; font-weight: 800; }
        .greeting { color: #FFD700; font-size: 1rem; font-weight: bold; text-shadow: 0 0 10px rgba(255, 215, 0, 0.2); }
        .twin-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 15px; }
        @media (max-width: 768px) { .twin-grid { grid-template-columns: 1fr; } }
        .twin-card { background: #0f172a; border-radius: 12px; border: 1px solid #1e293b; padding: 15px; }
        .twin-title { font-size: 0.8rem; color: #94a3b8; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; border-bottom: 1px solid #1e293b; padding-bottom: 6px; }
        .twin-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #1e293b; }
        .twin-row:last-child { border-bottom: none; }
        .twin-label { font-size: 0.85rem; font-weight: 600; color: #cbd5e1; }
        .twin-val { font-size: 0.95rem; font-weight: 700; }
        .up { color: #10b981 !important; }    
        .down { color: #ef4444 !important; }  
        .neutral { color: #cbd5e1 !important; }
        
        /* 🛠 FIXED GAUGES GRID CONFIG */
        .gauges-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 15px; width: 100%; }
        @media (max-width: 768px) { .gauges-grid { grid-template-columns: repeat(2, 1fr); } }
        @media (max-width: 480px) { .gauges-grid { grid-template-columns: 1fr; } }
        .gauge-panel { background: #0f172a; border-radius: 12px; padding: 12px; border: 1px solid #1e293b; text-align: center; width: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 140px; }
        .gauge-title { font-size: 0.75rem; color: #94a3b8; font-weight: 700; margin-bottom: 8px; text-transform: uppercase; width: 100%; border-bottom: 1px solid #1e293b; padding-bottom: 4px; }
        .gauge-chart-wrapper { width: 100%; max-width: 180px; height: auto; display: flex; justify-content: center; }

        .news-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px; }
        @media (max-width: 768px) { .news-grid { grid-template-columns: 1fr; } }
        .news-box { background: #0f172a; border-radius: 12px; border: 1px solid #1e293b; padding: 15px; min-height: 250px; display: flex; flex-direction: column; }
        .news-header { font-size: 0.9rem; font-weight: bold; padding-bottom: 6px; margin-bottom: 10px; border-bottom: 2px solid #334155; }
        .news-content { font-size: 0.85rem; color: #cbd5e1; line-height: 1.6; white-space: pre-line; flex-grow: 1; }
        .mops-badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-weight: bold; margin-bottom: 8px; font-size: 0.8rem; }
        .bg-up { background: rgba(16, 185, 129, 0.2); color: #10b981; }
        .bg-down { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
        footer { text-align: center; color: #ff4d4d; font-size: 0.9rem; font-weight: bold; padding: 12px; background: #0a0f1e; border-radius: 10px; border: 1px solid #ff4d4d; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div><h1>KYAW GYI INTELLIGENCE HUB ⚡ <span class="greeting">(မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ)</span></h1></div>
            <div style="color: #64748b; font-size: 0.8rem; font-weight: bold;">Last Sync: {{ data.last_update }}</div>
        </header>

        <div class="twin-grid">
            <div class="twin-card">
                <div class="twin-title">🪙 Markets & Currency Index</div>
                <div class="twin-row">
                    <span class="twin-label">Bitcoin (BTC)</span>
                    <span class="twin-val {{ data.trends.BTC }}">
                        {{ data.display_prices.BTC }} {% if data.trends.BTC == 'up' %}▲{% elif data.trends.BTC == 'down' %}▼{% endif %}
                    </span>
                </div>
                <div class="twin-row">
                    <span class="twin-label">Ethereum (ETH)</span>
                    <span class="twin-val {{ data.trends.ETH }}">
                        {{ data.display_prices.ETH }} {% if data.trends.ETH == 'up' %}▲{% elif data.trends.ETH == 'down' %}▼{% endif %}
                    </span>
                </div>
                <div class="twin-row">
                    <span class="twin-label">US Dollar Index (DXY)</span>
                    <span class="twin-val {{ data.trends.DXY }}">
                        {{ data.display_prices.DXY }} {% if data.trends.DXY == 'up' %}▲{% elif data.trends.DXY == 'down' %}▼{% endif %}
                    </span>
                </div>
            </div>

            <div class="twin-card">
                <div class="twin-title">🛢 Energies & Spot Gold</div>
                <div class="twin-row">
                    <span class="twin-label">WTI Crude Oil</span>
                    <span class="twin-val {{ data.trends.WTI }}">
                        {{ data.display_prices.WTI }} {% if data.trends.WTI == 'up' %}▲{% elif data.trends.WTI == 'down' %}▼{% endif %}
                    </span>
                </div>
                <div class="twin-row">
                    <span class="twin-label">Brent Crude Oil</span>
                    <span class="twin-val {{ data.trends.BRENT }}">
                        {{ data.display_prices.BRENT }} {% if data.trends.BRENT == 'up' %}▲{% elif data.trends.BRENT == 'down' %}▼{% endif %}
                    </span>
                </div>
                <div class="twin-row">
                    <span class="twin-label">Spot Gold (XAU/USD)</span>
                    <span class="twin-val {{ data.trends.GOLD }}">
                        {{ data.display_prices.GOLD }} {% if data.trends.GOLD == 'up' %}▲{% elif data.trends.GOLD == 'down' %}▼{% endif %}
                    </span>
                </div>
            </div>
        </div>

        <div class="gauges-grid">
            <div class="gauge-panel">
                <div class="gauge-title">🪙 Crypto F&G</div>
                <div class="gauge-chart-wrapper"><div id="cryptoGauge"></div></div>
            </div>
            <div class="gauge-panel">
                <div class="gauge-title">🟡 GOLD Spot</div>
                <div class="gauge-chart-wrapper"><div id="goldGauge"></div></div>
            </div>
            <div class="gauge-panel">
                <div class="gauge-title">🛢 WTI Crude</div>
                <div class="gauge-chart-wrapper"><div id="wtiGauge"></div></div>
            </div>
            <div class="gauge-panel">
                <div class="gauge-title">🔥 BRENT Oil</div>
                <div class="gauge-chart-wrapper"><div id="brentGauge"></div></div>
            </div>
        </div>

        <div class="news-grid">
            <div class="news-box">
                <div class="news-header" style="color: #60a5fa;">🤖 GOOD AI AUTOMATED MARKET ANALYSIS (မြန်မာလိုအနှစ်ချုပ်)</div>
                <div class="news-content">{{ data.ai_news }}</div>
            </div>

            <div class="news-box">
                <div class="news-header" style="color: #34d399;">📢 MEMBER DAILY MOPS TRACKER</div>
                {% if data.mops_trend != 'neutral' %}
                    <div class="mops-badge {% if data.mops_trend == 'up' %}bg-up{% else %}bg-down{% endif %}">
                        {% if data.mops_trend == 'up' %}▲ Singapore Price Up (စိမ်း){% else %}▼ Singapore Price Down (နီ){% endif %}
                    </div>
                {% endif %}
                <div class="news-content" style="background: #111827; padding: 12px; border-radius: 8px;">
                    {{ data.last_mops_text }}
                    <div style="font-size: 0.7rem; color: #64748b; margin-top: 10px; text-align: right; border-top: 1px solid #1e293b; padding-top: 6px;">
                        Updated by {{ data.last_mops_user }} at {{ data.last_mops_time }}
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
                chart: { type: 'radialBar', height: 140, sparkline: { enabled: true } },
                plotOptions: {
                    radialBar: {
                        startAngle: -90, endAngle: 90,
                        track: { background: '#1e293b', strokeWidth: '85%' },
                        dataLabels: {
                            name: { show: true, offsetY: 15, fontSize: '9px', color: '#64748b', fontWeight: 600 },
                            value: { offsetY: -12, fontSize: '12px', fontWeight: 700, color: '#ffffff',
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

bot = telebot.TeleBot(TG_TOKEN)

# ======= [ GEMINI AI ENGINE ] =======
def update_ai_analysis(prices):
    try:
        headlines = []
        rss_url = "https://www.investing.com/rss/news_287.rss"
        res = requests.get(rss_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        root = ET.fromstring(res.content)
        for item in root.findall('.//item')[:4]:
            headlines.append(item.find('title').text)
        
        raw_news = "\n".join(headlines) if headlines else "No external news headlines pulled."
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            f"မားကတ်အခြေအနေကို အောက်ပါဈေးနှုန်းများနှင့် သတင်းများအပေါ် မူတည်၍ မြန်မာလို ထိရောက်ပြတ်သားစွာ အနှစ်ချုပ်ပေးပါ။\n"
            f"BTC: {prices['BTC']}, Gold: {prices['GOLD']}, Oil: {prices['WTI']}, DXY: {prices['DXY']}\n"
            f"သတင်းခေါင်းစဉ်များ: {raw_news}\n"
            f"သတ်မှတ်ချက်: Bullet points ၄ ခုတိတိဖြင့် ထိရောက်စွာ အနှစ်ချုပ်ပါ။ စာလုံးရေ ၁၂၀ ဝန်းကျင်ခန့်သာ ရေးသားပါ။"
        )
        response = model.generate_content(prompt)
        return response.text if response.text else "စျေးကွက်သတင်းများကို ပုံမှန်အတိုင်း စောင့်ကြည့်လေ့လာနေပါသည်။"
    except:
        return f"⚠️ ကမ္ဘာ့သတင်းများနှင့် ဈေးကွက်ဒေတာများကို ပုံမှန်အတိုင်း Update လုပ်ပေးနေပါသည်။"

# ======= [ DATA CORE FETCH ENGINE ] =======
def get_market_data():
    prices = {"BTC": 0.0, "ETH": 0.0, "GOLD": 0.0, "WTI": 0.0, "BRENT": 0.0, "DXY": 0.0}
    disp = {"BTC": "$0.00", "ETH": "$0.00", "GOLD": "$0.00", "WTI": "$0.00", "BRENT": "$0.00", "DXY": "0.00"}
    trends = {"BTC": "neutral", "ETH": "neutral", "GOLD": "neutral", "WTI": "neutral", "BRENT": "neutral", "DXY": "neutral"}
    
    try:
        res = requests.get("https://min-api.cryptocompare.com/data/pricemultifull?fsyms=BTC,ETH,PAXG&tsyms=USD").json()
        for k, sym in [("BTC", "BTC"), ("ETH", "ETH"), ("GOLD", "PAXG")]:
            raw = res['RAW'][sym]['USD']
            prices[k] = raw['PRICE']
            disp[k] = f"${prices[k]:,.2f}"
            trends[k] = "up" if raw['CHANGEPCT24HOUR'] > 0 else "down"
    except: pass

    try:
        for k, ticker in [("WTI", "CL=F"), ("BRENT", "BZ=F"), ("DXY", "DX-Y.NYB")]:
            y_res = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1d").json()
            meta = y_res['chart']['result'][0]['meta']
            prices[k] = meta['regularMarketPrice']
            prev = meta['previousClose']
            disp[k] = f"${prices[k]:,.2f}" if k != "DXY" else f"{prices[k]:,.2f}"
            trends[k] = "up" if prices[k] > prev else "down"
    except: pass

    return prices, disp, trends

# Dashboard ဒေတာသီးသန့် Update လုပ်မယ့် Function
def update_dashboard_data():
    prices, disp, trends = get_market_data()
    current_market_cache["prices"] = prices
    current_market_cache["display_prices"] = disp
    current_market_cache["trends"] = trends
    current_market_cache["last_update"] = time.strftime("%I:%M %p")
    
    current_market_cache["crypto_gauge"] = 30 if trends["BTC"] == "down" else 75
    current_market_cache["gold_gauge"] = 70 if trends["GOLD"] == "up" else 40
    current_market_cache["wti_gauge"] = 65 if trends["WTI"] == "up" else 35
    current_market_cache["brent_gauge"] = 68 if trends["BRENT"] == "up" else 38

# ======= [ TELEGRAM CONSTRUCT REPORT ] =======
def generate_telegram_msg():
    d = current_market_cache["display_prices"]
    t = current_market_cache["trends"]
    def arr(k): return "▲" if t[k] == "up" else "▼"
    
    msg = (
        "✨ 🟡 **(မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ)** 🟡 ✨\n\n"
        "📊 **Market Intelligence Update**\n\n"
        f"🪙 **BTC:** {d['BTC']} {arr('BTC')} | **ETH:** {d['ETH']} {arr('ETH')}\n"
        f"🛢 **WTI:** {d['WTI']} {arr('WTI')} | **BRENT:** {d['BRENT']} {arr('BRENT')}\n"
        f"🟡 **GOLD:** {d['GOLD']} {arr('GOLD')} | 💵 **DXY:** {d['DXY']} {arr('DXY')}\n\n"
        f"🤖 **AI Analysis:**\n{current_market_cache['ai_news']}\n\n"
        f"🕒 Sync: {current_market_cache['last_update']}\n\n"
        "⚠️ **အရောင်းအဝယ်မပြုလုပ်ပါ သတင်းအချက်အလက်တင်ပြခြင်းပါ**"
    )
    return msg

@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    if m.text and any(kw in m.text.lower() for kw in ["mops", "singapore", "ဆီဈေး"]):
        num = [float(n) for n in re.findall(r"\d+\.\d+|\d+", m.text)]
        val = sum(num)/len(num) if num else 0
        if current_market_cache["prev_mops_val"] > 0:
            current_market_cache["mops_trend"] = "up" if val > current_market_cache["prev_mops_val"] else "down"
        current_market_cache["prev_mops_val"] = val
        current_market_cache["last_mops_text"] = m.text
        current_market_cache["last_mops_user"] = m.from_user.first_name or "Member"
        current_market_cache["last_mops_time"] = time.strftime("%I:%M %p")
    
    if m.text and "ဈေး" in m.text:
        bot.reply_to(m, generate_telegram_msg())

# 🛠 [ TIMERS SPLIT WORKER ] 🛠
# 1. Dashboard အတွက် ၁၅ မိနစ်တစ်ခါ Update စစ်မယ့်စနစ်
def dashboard_loop():
    while True:
        update_dashboard_data()
        time.sleep(900)  # 15 မိနစ် (15 * 60 စက္ကန့်)

# 2. Telegram အတွက် ၄ နာရီတစ်ခါ သီးသန့်ထုတ်လုပ်ပို့ပေးမယ့်စနစ်
def telegram_loop():
    while True:
        # ပို့ခါနီးမှ နောက်ဆုံးရ AI သတင်းကို Update ယူသည်
        current_market_cache["ai_news"] = update_ai_analysis(current_market_cache["prices"])
        try:
            bot.send_message(GROUP_CHAT_ID, generate_telegram_msg())
        except:
            pass
        time.sleep(14400) # 4 နာရီ (4 * 3600 စက္ကန့်)

if __name__ == "__main__":
    update_dashboard_data() # စက်စဖွင့်ချင်း Data ချက်ချင်းဆွဲတင်ရန်
    current_market_cache["ai_news"] = update_ai_analysis(current_market_cache["prices"])
    
    threading.Thread(target=dashboard_loop, daemon=True).start()
    threading.Thread(target=telegram_loop, daemon=True).start()
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    
    while True:
        try:
            bot.polling(none_stop=True)
        except:
            time.sleep(5)
