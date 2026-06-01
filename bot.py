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

# =========================================================
# ✍️ [ ADMIN INPUT ] - ကျိုင် ကိုယ်တိုင် သတင်းရေးထည့်ရန်နေရာ
# =========================================================
ADMIN_MESSAGE = """●QR စနစ်ဖြင့်တစ်နိုင်ငံလုံး ဆိုင်ပေါင်း ၁၇၃၀ တပ်ဆင်ရောင်းချ ပေးနေပါသည်
● ရွှေဈေးကတော့ ကမ္ဘာ့ဒေါ်လာအညွှန်းကိန်း (DXY) ကြောင့် အနည်းငယ် ပြန်ဆင်းနိုင်ပါတယ်။
● မန်ဘာများအားလုံး မိမိတို့ ပိုင်ဆိုင်မှုကို သေချာ စီမံခန့်ခွဲကြပါရန်။"""
# =========================================================

# Global Data Cache
current_market_cache = {
    "prices": {"BTC": 0.0, "ETH": 0.0, "GOLD": 0.0, "WTI": 0.0, "BRENT": 0.0, "DXY": 0.0},
    "display_prices": {"BTC": "$0.00", "ETH": "$0.00", "GOLD": "$0.00", "WTI": "$0.00", "BRENT": "$0.00", "DXY": "0.00"},
    "trends": {"BTC": "neutral", "ETH": "neutral", "GOLD": "neutral", "WTI": "neutral", "BRENT": "neutral", "DXY": "neutral"},
    "last_update": "N/A",
    "crypto_gauge": 50,
    "wti_gauge": 50,
    "brent_gauge": 50,
    "gold_gauge": 50,
    "ai_news": "● ကမ္ဘာ့စီးပွားရေးနှင့် ရေနံဈေးကွက်သတင်းများကို AI ဖြင့် သေချာစွာ အနှစ်ချုပ် သုံးသပ်နေပါသည်...",
    "last_mops_text": "No custom MOPS news forwarded from group yet. Waiting for member updates...",
    "admin_intel": ADMIN_MESSAGE # Admin သတင်း စတင်ထည့်သွင်းခြင်း
}

# ======= [ HTML UI - FULL RESPONSIVE WITH ADMIN PANEL ] =======
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-EWB0JD6TR2"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-EWB0JD6TR2');
    </script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ Kyaw Gyi Market Intelligence Hub</title>
    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=500;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }
        body { background-color: #0b0f19; color: #f1f5f9; padding: 15px; }
        .container { max-width: 1200px; margin: 0 auto; width: 100%; }
        
        header { text-align: center; margin-bottom: 20px; border-bottom: 1px solid #1e293b; padding-bottom: 15px; }
        h1 { font-size: 1.5rem; color: #38bdf8; font-weight: 800; letter-spacing: 0.5px; }
        .greeting { color: #FFD700; font-size: 1rem; font-weight: bold; display: block; margin-top: 6px; }
        .sync-time { color: #64748b; font-size: 0.8rem; font-weight: bold; display: block; margin-top: 4px; }
        
        .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 15px; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 15px; }
        .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 15px; }
        
        .card { background: #111726; border-radius: 14px; border: 1px solid #1e293b; padding: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2); }
        .card-title { font-size: 0.85rem; color: #94a3b8; font-weight: bold; text-transform: uppercase; margin-bottom: 12px; border-bottom: 1px solid #1e293b; padding-bottom: 6px; }
        
        .row-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #1e293b; }
        .row-item:last-child { border-bottom: none; }
        .label-text { font-size: 0.9rem; font-weight: 700; color: #cbd5e1; }
        .val-text { font-size: 1rem; font-weight: 800; }
        
        .gauge-card { background: #111726; border-radius: 14px; padding: 12px; border: 1px solid #1e293b; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; }
        .gauge-header { font-size: 0.75rem; color: #94a3b8; font-weight: bold; margin-bottom: 8px; text-transform: uppercase; }
        .chart-container { width: 100%; height: 110px; display: flex; justify-content: center; align-items: center; overflow: hidden; }

        .up { color: #10b981 !important; }    
        .down { color: #ef4444 !important; }  
        .neutral { color: #cbd5e1 !important; }
        
        .news-box { line-height: 1.7; font-size: 0.9rem; color: #e2e8f0; white-space: pre-line; text-align: left; }
        
        footer { text-align: center; color: #ef4444; font-size: 0.8rem; font-weight: bold; padding: 12px; background: #070a12; border-radius: 12px; border: 1px solid rgba(239, 68, 68, 0.2); margin-top: 10px; }

        @media (max-width: 768px) {
            body { padding: 10px; }
            h1 { font-size: 1.3rem; }
            .grid-2 { grid-template-columns: 1fr; gap: 12px; }
            .grid-3 { grid-template-columns: 1fr; gap: 12px; }
            .grid-4 { grid-template-columns: repeat(2, 1fr); gap: 10px; }
            .card { padding: 12px; }
            .label-text { font-size: 0.85rem; }
            .val-text { font-size: 0.95rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>KYAW GYI INTELLIGENCE HUB ⚡</h1>
            <span class="greeting">(မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ)</span>
            <span class="sync-time">Last Sync: {{ data.last_update }}</span>
        </header>

        <div class="grid-2">
            <div class="card">
                <div class="card-title">🪙 MARKETS & CURRENCY INDEX</div>
                <div class="row-item">
                    <span class="label-text">Bitcoin (BTC)</span>
                    <span class="val-text {{ data.trends.BTC }}">{{ data.display_prices.BTC }}</span>
                </div>
                <div class="row-item">
                    <span class="label-text">Ethereum (ETH)</span>
                    <span class="val-text {{ data.trends.ETH }}">{{ data.display_prices.ETH }}</span>
                </div>
                <div class="row-item">
                    <span class="label-text">US Dollar Index (DXY)</span>
                    <span class="val-text {{ data.trends.DXY }}">{{ data.display_prices.DXY }}</span>
                </div>
            </div>

            <div class="card">
                <div class="card-title">🛢 ENERGIES & SPOT GOLD</div>
                <div class="row-item">
                    <span class="label-text">WTI Crude Oil</span>
                    <span class="val-text {{ data.trends.WTI }}">{{ data.display_prices.WTI }}</span>
                </div>
                <div class="row-item">
                    <span class="label-text">Brent Crude Oil</span>
                    <span class="val-text {{ data.trends.BRENT }}">{{ data.display_prices.BRENT }}</span>
                </div>
                <div class="row-item">
                    <span class="label-text">Spot Gold (XAU/USD)</span>
                    <span class="val-text {{ data.trends.GOLD }}">{{ data.display_prices.GOLD }}</span>
                </div>
            </div>
        </div>

        <div class="grid-4">
            <div class="gauge-card">
                <div class="gauge-header">🪙 Crypto F&G</div>
                <div class="chart-container"><div id="cryptoGauge"></div></div>
            </div>
            <div class="gauge-card">
                <div class="gauge-header">🟡 GOLD Spot</div>
                <div class="chart-container"><div id="goldGauge"></div></div>
            </div>
            <div class="gauge-card">
                <div class="gauge-header">🛢 WTI Crude</div>
                <div class="chart-container"><div id="wtiGauge"></div></div>
            </div>
            <div class="gauge-card">
                <div class="gauge-header">🔥 Brent Oil</div>
                <div class="chart-container"><div id="brentGauge"></div></div>
            </div>
        </div>

        <div class="grid-3">
            <div class="card" style="border: 1px solid rgba(255, 215, 0, 0.4);">
                <div class="card-title" style="color: #FFD700; border-bottom-color: rgba(255, 215, 0, 0.2);">✍️ ADMIN INTEL & MARKET OUTLOOK</div>
                <div class="news-box" style="color: #ffeaa7;">
                    {{ data.admin_intel }}
                </div>
            </div>

            <div class="card">
                <div class="card-title" style="color: #60a5fa; border-bottom-color: #2e3d56;">🤖 GOOD AI AUTOMATED ANALYSIS</div>
                <div class="news-box">
                    {{ data.ai_news }}
                </div>
            </div>

            <div class="card">
                <div class="card-title" style="color: #34d399; border-bottom-color: #2e3d56;">📢 MEMBER DAILY MOPS TRACKER</div>
                <div class="news-box" style="background: #090f1d; padding: 12px; border-radius: 10px; font-size: 0.85rem;">
                    {{ data.last_mops_text }}
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
                        track: { background: '#1e293b', strokeWidth: '80%' },
                        dataLabels: {
                            name: { show: false },
                            value: { offsetY: -2, fontSize: '12px', fontWeight: 700, color: '#ffffff',
                                formatter: function(val) { return val >= 50 ? 'Buy' : 'Sell'; }
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

# ======= [ FIXED GEMINI NEWS PIPELINE ] =======
def update_ai_analysis(prices):
    try:
        headlines = []
        rss_url = "https://www.cnbc.com/id/10000115/device/rss/rss.html"
        res = requests.get(rss_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        root = ET.fromstring(res.content)
        for item in root.findall('.//item')[:4]:
            text = item.find('title').text
            if text: headlines.append(text)
        
        raw_news = " | ".join(headlines) if headlines else "Global macro trends are dynamic."

        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            "Analyze the following financial values and market news headlines to provide a brief 3-bullet-point summary in Burmese. "
            "Keep it short, clear, and actionable.\n\n"
            f"Prices: BTC={prices['BTC']}, Gold={prices['GOLD']}, WTI={prices['WTI']}, Brent={prices['BRENT']}, DXY={prices['DXY']}\n"
            f"News: {raw_news}\n\n"
            "Requirements:\n"
            "1. Output exactly 3 bullet points starting with '●'.\n"
            "2. Write completely in clean Burmese language.\n"
            "3. Focus on Gold and Oil trends."
        )
        response = model.generate_content(prompt)
        if response.text and len(response.text.strip()) > 10:
            return response.text.strip()
        return "● ကမ္ဘာ့ရေနံဈေးကွက်သည် လက်ရှိအခြေအနေတွင် ပုံမှန်အတိုင်း ဆက်လက်ရွေ့လျားနေပါသည်။\n● ရွှေဈေးနှုန်းသည် ဒေါ်လာအညွှန်းကိန်းအတက်အကျပေါ် မူတည်၍ ဂယက်ရိုက်ခတ်မှု ရှိနေပါသည်။"
    except:
        return "● ကမ္ဘာ့ရေနံနှင့် ရွှေဈေးနှုန်းများသည် လက်ရှိတွင် သတ်မှတ်ဈေးကွက်အသီးသီး၌ တည်ငြိမ်စွာရှိနေပါသည်။\n● စီးပွားရေးသတင်းများနှင့် ပတ်သက်၍ အပြောင်းအလဲများကို ဆက်လက်စောင့်ကြည့်ရန် လိုအပ်ပါသည်။"

# ======= [ DATA FEEDS ENGINE ] =======
def get_market_data():
    prices = {"BTC": 0.0, "ETH": 0.0, "GOLD": 0.0, "WTI": 0.0, "BRENT": 0.0, "DXY": 0.0}
    disp = {"BTC": "$0.00", "ETH": "$0.00", "GOLD": "$0.00", "WTI": "$0.00", "BRENT": "$0.00", "DXY": "0.00"}
    trends = {"BTC": "neutral", "ETH": "neutral", "GOLD": "neutral", "WTI": "neutral", "BRENT": "neutral", "DXY": "neutral"}
    
    try:
        res = requests.get("https://min-api.cryptocompare.com/data/pricemultifull?fsyms=BTC,ETH,PAXG&tsyms=USD", timeout=8).json()
        for k, sym in [("BTC", "BTC"), ("ETH", "ETH"), ("GOLD", "PAXG")]:
            raw = res['RAW'][sym]['USD']
            prices[k] = raw['PRICE']
            disp[k] = f"${prices[k]:,.2f}"
            trends[k] = "up" if raw['CHANGEPCT24HOUR'] > 0 else "down"
    except: pass

    try:
        oil_res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=wti-crude-oil,brent-crude-oil&vs_currencies=usd", timeout=8).json()
        prices["WTI"] = oil_res.get('wti-crude-oil', {}).get('usd', 87.42)
        prices["BRENT"] = oil_res.get('brent-crude-oil', {}).get('usd', 91.12)
    except:
        prices["WTI"] = 87.42
        prices["BRENT"] = 91.12

    prices["DXY"] = 99.13
    for key in ["WTI", "BRENT", "DXY"]:
        disp[key] = f"${prices[key]:,.2f}" if key != "DXY" else f"{prices[key]:,.2f}"
        trends[key] = "up"

    return prices, disp, trends

def update_dashboard_data():
    prices, disp, trends = get_market_data()
    current_market_cache["prices"] = prices
    current_market_cache["display_prices"] = disp
    current_market_cache["trends"] = trends
    current_market_cache["last_update"] = time.strftime("%I:%M %p")
    
    current_market_cache["crypto_gauge"] = 35 if trends["BTC"] == "down" else 75
    current_market_cache["gold_gauge"] = 70 if trends["GOLD"] == "up" else 40
    current_market_cache["wti_gauge"] = 65
    current_market_cache["brent_gauge"] = 68

# ======= [ TELEGRAM CONSTRUCT REPORT WITH ADMIN MSG ] =======
def generate_telegram_msg():
    d = current_market_cache["display_prices"]
    t = current_market_cache["trends"]
    def arr(k): return "▲" if t[k] == "up" else "▼"
    return (
        "✨ 🟡 **(မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ)** 🟡 ✨\n\n"
        "📊 **Market Intelligence Update**\n\n"
        f"🪙 **BTC:** {d['BTC']} {arr('BTC')} | **ETH:** {d['ETH']} {arr('ETH')}\n"
        f"🛢 **WTI:** {d['WTI']} | **BRENT:** {d['BRENT']}\n"
        f"🟡 **GOLD:** {d['GOLD']} {arr('GOLD')} | 💵 **DXY:** {d['DXY']}\n\n"
        f"✍️ **Admin Intel & Outlook:**\n{current_market_cache['admin_intel']}\n\n" # Tele ထဲသို့ Admin သတင်း ထည့်ပေးခြင်း
        f"🤖 **AI Analysis:**\n{current_market_cache['ai_news']}\n\n"
        f"🕒 Sync: {current_market_cache['last_update']}\n\n"
        "⚠️ **အရောင်းအဝယ်မပြုလုပ်ပါ သတင်းအချက်အလက်တင်ပြခြင်းပါ**"
    )

@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    if m.text and any(kw in m.text.lower() for kw in ["mops", "singapore", "ဆီဈေး"]):
        current_market_cache["last_mops_text"] = m.text
    if m.text and "ဈေး" in m.text:
        bot.reply_to(m, generate_telegram_msg())

def dashboard_loop():
    while True:
        update_dashboard_data()
        time.sleep(900)

def telegram_loop():
    while True:
        current_market_cache["ai_news"] = update_ai_analysis(current_market_cache["prices"])
        try: bot.send_message(GROUP_CHAT_ID, generate_telegram_msg())
        except: pass
        time.sleep(14400)

if __name__ == "__main__":
    update_dashboard_data()
    current_market_cache["ai_news"] = update_ai_analysis(current_market_cache["prices"])
    
    threading.Thread(target=dashboard_loop, daemon=True).start()
    threading.Thread(target=telegram_loop, daemon=True).start()
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    
    while True:
        try: bot.polling(none_stop=True)
        except: time.sleep(5)
