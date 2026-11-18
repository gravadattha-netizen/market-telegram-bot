import time
import re
import requests
import threading
import os
import xml.etree.ElementTree as ET
from flask import Flask, render_template_string
import telebot
import google.generativeai as genai

app = Flask('')

# ======= [ CONFIGURATION - TOKENS & KEYS ] =======
TG_TOKEN = "8876036329:AAHSip397-NucbnJIX9aK9d2jeNo115gsX8" 
GROUP_CHAT_ID = -1003940722388  
GOOGLE_API_KEY = "AIzaSyAKM5IAugwBdKxrWQ__igkDwjwITW6f2kc"

genai.configure(api_key=GOOGLE_API_KEY)

# =========================================================
# ✍️ [ ADMIN INPUT ] - ဆီလုပ်ငန်းသတင်းများ ရေးထည့်ရန်နေရာ
# =========================================================
ADMIN_MESSAGE = """● QR စနစ်ဖြင့်တစ်နိုင်ငံလုံး ဆိုင်ပေါင်း ၁၉၂၇ ဆိုင်တပ်ဆင်ရောင်းချ ပေးနေပါသည်
● မန်ဘာများအားလုံး မိမိတို့ ပိုင်ဆိုင်မှုကို သေချာ စီမံခန့်ခွဲကြပါရန်။"""
# =========================================================

# Global Data Cache (စတင်ချိန်တွင် ပြသမည့် MOPS ဈေးနှုန်းများ)
current_market_cache = {
    "prices": {"WTI": 71.70, "BRENT": 76.00},
    "display_prices": {"WTI": "$71.70", "BRENT": "$76.00"},
    "trends": {"WTI": "up", "BRENT": "up"},
    
    # MOPS Data Cache (Dynamic Update ဖြစ်မည့်နေရာ)
    "mops_prices": {"MOGAS": 97.24, "GASOLINE": 153.30},
    "mops_display": {"MOGAS": "$97.24", "GASOLINE": "$153.30"},
    "mops_signals": {"MOGAS": "SELL ▼", "GASOLINE": "SELL ▼"},
    "mops_ta": {"MOGAS": "STRONG SELL", "GASOLINE": "SELL"},

    "last_update": "N/A",
    "wti_gauge": 65,
    "brent_gauge": 68,
    "mogas_gauge": 30,
    "diesel_gauge": 35,
    "ai_news": "● ကမ္ဘာ့ရေနံဈေးကွက်သတင်းများကို AI ဖြင့် သေချာစွာ အနှစ်ချုပ် သုံးသပ်နေပါသည်...",
    "last_mops_text": "No custom MOPS news forwarded from group yet. Waiting for member updates...",
    "admin_intel": ADMIN_MESSAGE 
}

# ======= [ HTML UI - MODERN REDESIGNED DASHBOARD ] =======
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
    <title>⚡ Kyaw Gyi Energy Intelligence Hub</title>
    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }
        body { background: linear-gradient(135deg, #070b14 0%, #0f172a 100%); color: #f8fafc; padding: 20px; min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; width: 100%; }
        
        header { text-align: center; margin-bottom: 25px; border-bottom: 1px solid rgba(56, 189, 248, 0.2); padding-bottom: 20px; background: rgba(17, 23, 38, 0.7); backdrop-filter: blur(10px); border-radius: 16px; padding: 20px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3); }
        h1 { font-size: 1.6rem; color: #38bdf8; font-weight: 800; letter-spacing: 0.8px; text-transform: uppercase; text-shadow: 0 2px 10px rgba(56,189,248,0.3); }
        .greeting { color: #fbbf24; font-size: 1rem; font-weight: 700; display: block; margin-top: 8px; }
        .sync-time { color: #94a3b8; font-size: 0.8rem; font-weight: 600; display: block; margin-top: 6px; }

        .section-title { font-size: 1rem; color: #38bdf8; font-weight: 800; text-align: center; margin: 20px 0 12px 0; text-transform: uppercase; letter-spacing: 1px; display: flex; align-items: center; justify-content: center; gap: 8px; }
        
        .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 15px; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 15px; }
        
        .card { background: rgba(17, 23, 38, 0.85); backdrop-filter: blur(12px); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08); padding: 18px; box-shadow: 0 8px 20px -4px rgba(0,0,0,0.4); text-align: center; transition: transform 0.2s ease, border-color 0.2s ease; }
        .card:hover { border-color: rgba(56, 189, 248, 0.4); transform: translateY(-2px); }
        .card-title { font-size: 0.85rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; margin-bottom: 10px; letter-spacing: 0.5px; }
        .price-val { font-size: 1.6rem; font-weight: 800; color: #ffffff; margin-bottom: 12px; text-shadow: 0 2px 8px rgba(0,0,0,0.5); }
        
        .badge { display: inline-block; padding: 6px 14px; border-radius: 30px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }
        .badge-buy { background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: #ffffff; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); }
        .badge-sell { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: #ffffff; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3); }

        .gauge-card { background: rgba(17, 23, 38, 0.85); backdrop-filter: blur(12px); border-radius: 16px; padding: 14px; border: 1px solid rgba(255, 255, 255, 0.08); text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; box-shadow: 0 8px 20px -4px rgba(0,0,0,0.4); }
        .gauge-header { font-size: 0.75rem; color: #94a3b8; font-weight: 700; margin-bottom: 5px; text-transform: uppercase; }
        .chart-container { width: 100%; height: 120px; display: flex; justify-content: center; align-items: center; overflow: hidden; }

        .ta-dashboard { background: rgba(17, 23, 38, 0.9); border: 1px solid rgba(251, 191, 36, 0.3); border-radius: 16px; padding: 18px; margin-bottom: 20px; box-shadow: 0 8px 20px -4px rgba(0,0,0,0.4); }
        .ta-title { font-size: 0.9rem; color: #fbbf24; font-weight: 800; text-align: center; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
        .ta-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
        .ta-item { background: rgba(11, 15, 25, 0.6); padding: 10px 14px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; border: 1px solid rgba(255,255,255,0.05); }
        .ta-label { font-size: 0.8rem; color: #cbd5e1; font-weight: 700; }
        .ta-val { font-size: 0.85rem; font-weight: 800; color: #38bdf8; }

        .news-card-title { font-size: 0.85rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 8px; text-align: left; }
        .news-box { line-height: 1.7; font-size: 0.9rem; color: #e2e8f0; white-space: pre-line; text-align: left; }
        
        footer { text-align: center; color: #ef4444; font-size: 0.8rem; font-weight: 700; padding: 14px; background: rgba(7, 10, 18, 0.9); border-radius: 12px; border: 1px solid rgba(239, 68, 68, 0.3); margin-top: 15px; letter-spacing: 0.5px; }

        @media (max-width: 768px) {
            body { padding: 10px; }
            h1 { font-size: 1.3rem; }
            .grid-2 { grid-template-columns: 1fr; gap: 12px; }
            .grid-3 { grid-template-columns: 1fr; gap: 12px; }
            .ta-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Oil Energy Intelligence Hub</h1>
            <span class="greeting">(မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ)</span>
            <span class="sync-time">Last Sync: {{ data.last_update }}</span>
        </header>

        <div class="section-title">📊 Live Market Prices & MOPS Update</div>
        
        <!-- Live Prices Cards -->
        <div class="grid-2">
            <div class="card">
                <div class="card-title">WTI Crude</div>
                <div class="price-val">{{ data.display_prices.WTI }}</div>
                <div><span class="badge {{ 'badge-buy' if data.trends.WTI == 'up' else 'badge-sell' }}">{{ 'BUY ▲' if data.trends.WTI == 'up' else 'SELL ▼' }}</span></div>
            </div>
            <div class="card">
                <div class="card-title">Brent Oil</div>
                <div class="price-val">{{ data.display_prices.BRENT }}</div>
                <div><span class="badge {{ 'badge-buy' if data.trends.BRENT == 'up' else 'badge-sell' }}">{{ 'BUY ▲' if data.trends.BRENT == 'up' else 'SELL ▼' }}</span></div>
            </div>
        </div>

        <div class="grid-2">
            <div class="card">
                <div class="card-title">MOPS MOGAS (N1B2!)</div>
                <div class="price-val" style="color: #38bdf8;">{{ data.mops_display.MOGAS }}</div>
                <div><span class="badge {{ 'badge-buy' if 'BUY' in data.mops_signals.MOGAS else 'badge-sell' }}">{{ data.mops_signals.MOGAS }}</span></div>
            </div>
            <div class="card">
                <div class="card-title">MOPS DIESEL 10PPM (SGB1!)</div>
                <div class="price-val" style="color: #38bdf8;">{{ data.mops_display.GASOLINE }}</div>
                <div><span class="badge {{ 'badge-buy' if 'BUY' in data.mops_signals.GASOLINE else 'badge-sell' }}">{{ data.mops_signals.GASOLINE }}</span></div>
            </div>
        </div>

        <!-- 4 GAUGES SECTION -->
        <div class="section-title">📈 Market Sentiment Gauges</div>
        <div class="grid-2">
            <div class="gauge-card">
                <div class="gauge-header">🛢 WTI Crude Gauge</div>
                <div class="chart-container"><div id="wtiGauge"></div></div>
            </div>
            <div class="gauge-card">
                <div class="gauge-header">🔥 Brent Oil Gauge</div>
                <div class="chart-container"><div id="brentGauge"></div></div>
            </div>
        </div>
        <div class="grid-2" style="margin-top: 15px;">
            <div class="gauge-card">
                <div class="gauge-header">⛽ MOPS MOGAS Gauge</div>
                <div class="chart-container"><div id="mogasGauge"></div></div>
            </div>
            <div class="gauge-card">
                <div class="gauge-header">🚛 MOPS DIESEL Gauge</div>
                <div class="chart-container"><div id="dieselGauge"></div></div>
            </div>
        </div>

        <!-- TECHNICAL ANALYSIS (TA) DASHBOARD SECTION -->
        <div class="ta-dashboard" style="margin-top: 20px;">
            <div class="ta-title">📐 Technical Analysis & Indicators Summary (TA)</div>
            <div class="ta-grid">
                <div class="ta-item">
                    <span class="ta-label">MOGAS Recommendation</span>
                    <span class="ta-val" style="color: {{ '#10b981' if 'BUY' in data.mops_ta.MOGAS else '#ef4444' }};">{{ data.mops_ta.MOGAS }}</span>
                </div>
                <div class="ta-item">
                    <span class="ta-label">DIESEL Recommendation</span>
                    <span class="ta-val" style="color: {{ '#10b981' if 'BUY' in data.mops_ta.GASOLINE else '#ef4444' }};">{{ data.mops_ta.GASOLINE }}</span>
                </div>
                <div class="ta-item">
                    <span class="ta-label">Market Momentum</span>
                    <span class="ta-val" style="color: #38bdf8;">Live Sync Active</span>
                </div>
                <div class="ta-item">
                    <span class="ta-label">Overall Trend Strength</span>
                    <span class="ta-val" style="color: #fbbf24;">Auto-Tracked</span>
                </div>
            </div>
        </div>

        <!-- Admin, AI & Member News -->
        <div class="grid-3">
            <div class="card" style="border: 1px solid rgba(255, 215, 0, 0.3); text-align: left;">
                <div class="news-card-title" style="color: #FFD700;">✍️ ADMIN INTEL & OUTLOOK</div>
                <div class="news-box" style="color: #fef08a;">
                    {{ data.admin_intel }}
                </div>
            </div>

            <div class="card" style="text-align: left;">
                <div class="news-card-title" style="color: #60a5fa;">🤖 OIL MARKET AI ANALYSIS</div>
                <div class="news-box">
                    {{ data.ai_news }}
                </div>
            </div>

            <div class="card" style="text-align: left;">
                <div class="news-card-title" style="color: #34d399;">📢 MEMBER DAILY MOPS TRACKER</div>
                <div class="news-box" style="background: rgba(9, 15, 29, 0.6); padding: 12px; border-radius: 10px; font-size: 0.85rem;">
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
                chart: { type: 'radialBar', height: 130, sparkline: { enabled: true } },
                plotOptions: {
                    radialBar: {
                        startAngle: -90, endAngle: 90,
                        track: { background: '#1e293b', strokeWidth: '75%' },
                        dataLabels: {
                            name: { show: false },
                            value: { offsetY: -2, fontSize: '12px', fontWeight: 700, color: '#ffffff',
                                formatter: function(val) { return val >= 50 ? 'Bullish' : 'Bearish'; }
                            }
                        }
                    }
                },
                fill: { colors: [getGaugeColor(value)] },
                labels: [labelText],
                theme: { mode: 'dark' }
            };
        }
        new ApexCharts(document.querySelector("#wtiGauge"), createGaugeOptions({{ data.wti_gauge }}, 'WTI')).render();
        new ApexCharts(document.querySelector("#brentGauge"), createGaugeOptions({{ data.brent_gauge }}, 'BRENT')).render();
        new ApexCharts(document.querySelector("#mogasGauge"), createGaugeOptions({{ data.mogas_gauge }}, 'MOGAS')).render();
        new ApexCharts(document.querySelector("#dieselGauge"), createGaugeOptions({{ data.diesel_gauge }}, 'DIESEL')).render();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(DASHBOARD_HTML, data=current_market_cache)

bot = telebot.TeleBot(TG_TOKEN)

# ======= [ DYNAMIC MOPS UPDATE FUNCTION ] =======
def apply_mops_update(new_mogas=None, new_diesel=None):
    if new_mogas is not None:
        old_mogas = current_market_cache["mops_prices"]["MOGAS"]
        is_up = new_mogas >= old_mogas
        current_market_cache["mops_prices"]["MOGAS"] = round(new_mogas, 2)
        current_market_cache["mops_display"]["MOGAS"] = f"${new_mogas:,.2f}"
        current_market_cache["mops_signals"]["MOGAS"] = "BUY ▲" if is_up else "SELL ▼"
        current_market_cache["mops_ta"]["MOGAS"] = "STRONG BUY" if is_up else "STRONG SELL"
        current_market_cache["mogas_gauge"] = 70 if is_up else 30

    if new_diesel is not None:
        old_diesel = current_market_cache["mops_prices"]["GASOLINE"]
        is_up = new_diesel >= old_diesel
        current_market_cache["mops_prices"]["GASOLINE"] = round(new_diesel, 2)
        current_market_cache["mops_display"]["GASOLINE"] = f"${new_diesel:,.2f}"
        current_market_cache["mops_signals"]["GASOLINE"] = "BUY ▲" if is_up else "SELL ▼"
        current_market_cache["mops_ta"]["GASOLINE"] = "BUY" if is_up else "SELL"
        current_market_cache["diesel_gauge"] = 68 if is_up else 35

# ======= [ GEMINI AI ANALYSIS ] =======
def update_ai_analysis(prices):
    try:
        headlines = []
        rss_url = "https://www.cnbc.com/id/19832390/device/rss/rss.html"
        res = requests.get(rss_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        root = ET.fromstring(res.content)
        for item in root.findall('.//item')[:4]:
            text = item.find('title').text
            if text: headlines.append(text)
        
        raw_news = " | ".join(headlines) if headlines else "Oil market metrics are shifting."

        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            "Analyze the following oil prices and energy market news to provide a brief 3-bullet-point summary in Burmese. "
            "Keep it short, clear, and highly focused on petroleum/crude oil trends.\n\n"
            f"Prices: WTI={prices['WTI']}, Brent={prices['BRENT']}, MOPS_MOGAS={current_market_cache['mops_prices']['MOGAS']}, MOPS_DIESEL={current_market_cache['mops_prices']['GASOLINE']}\n"
            f"News: {raw_news}\n\n"
            "Requirements:\n"
            "1. Output exactly 3 bullet points starting with '●'.\n"
            "2. Write completely in clean Burmese language.\n"
            "3. Do NOT mention gold, cryptocurrency, bitcoin, or currency indexes."
        )
        response = model.generate_content(prompt)
        if response.text and len(response.text.strip()) > 10:
            return response.text.strip()
    except Exception as e:
        print(f"Gemini error: {e}")
    return "● ကမ္ဘာ့ရေနံဈေးကွက်သည် လက်ရှိအခြေအနေတွင် ပုံမှန်အတိုင်း ဆက်လက်ရွေ့လျားနေပါသည်။\n● နိုင်ငံတကာစွမ်းအင်လိုအပ်ချက်နှင့် ထုတ်လုပ်မှုအခြေအနေများကို စောင့်ကြည့်ရပါမည်။"

# ======= [ YAHOO FINANCE LIVE FEED ] =======
def fetch_yahoo_oil_price(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=7).json()
        meta = response['chart']['result'][0]['meta']
        price = meta['regularMarketPrice']
        prev_close = meta['previousClose']
        trend = "up" if price >= prev_close else "down"
        return round(float(price), 2), trend
    except Exception as e:
        print(f"Yahoo Finance error for {symbol}: {e}")
        return None, None

def update_dashboard_data():
    prices = current_market_cache["prices"].copy()
    disp = current_market_cache["display_prices"].copy()
    trends = current_market_cache["trends"].copy()
    
    # 1. WTI Crude
    wti_p, wti_t = fetch_yahoo_oil_price("CL=F")
    if wti_p:
        prices["WTI"] = wti_p
        trends["WTI"] = wti_t
        
    # 2. Brent Crude
    brent_p, brent_t = fetch_yahoo_oil_price("BZ=F")
    if brent_p:
        prices["BRENT"] = brent_p
        trends["BRENT"] = brent_t
    else:
        prices["BRENT"] = round(prices["WTI"] + 4.10, 2)
        trends["BRENT"] = trends["WTI"]

    for key in ["WTI", "BRENT"]:
        disp[key] = f"${prices[key]:,.2f}"

    # Cache Update (MOPS ဈေးနှုန်းများကို Reset မချဘဲ လက်ရှိ Update ဖြစ်ထားသည့်အတိုင်း ဆက်ထိန်းထားမည်)
    current_market_cache["prices"] = prices
    current_market_cache["display_prices"] = disp
    current_market_cache["trends"] = trends

    current_market_cache["last_update"] = time.strftime("%I:%M %p")
    current_market_cache["wti_gauge"] = 65 if trends["WTI"] == "up" else 45
    current_market_cache["brent_gauge"] = 68 if trends["BRENT"] == "up" else 48

# ======= [ TELEGRAM CONSTRUCT REPORT ] =======
def generate_telegram_msg():
    d = current_market_cache["display_prices"]
    t = current_market_cache["trends"]
    mops_d = current_market_cache["mops_display"]
    mops_s = current_market_cache["mops_signals"]
    mops_ta = current_market_cache["mops_ta"]

    return (
        "✨ 🛢 **(မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ)** 🛢 ✨\n\n"
        "📊 **Energy Market Intelligence Update**\n\n"
        "🌍 **Live Market Prices:**\n"
        f"• **WTI Crude:** {d['WTI']} ({'BUY' if t['WTI']=='up' else 'SELL'})\n"
        f"• **Brent Oil:** {d['BRENT']} ({'BUY' if t['BRENT']=='up' else 'SELL'})\n"
        f"• **MOPS MOGAS:** {mops_d['MOGAS']} ({mops_s['MOGAS']}) | TA: `{mops_ta['MOGAS']}`\n"
        f"• **MOPS DIESEL 10PPM:** {mops_d['GASOLINE']} ({mops_s['GASOLINE']}) | TA: `{mops_ta['GASOLINE']}`\n\n"
        f"✍️ **Admin Intel & Outlook:**\n{current_market_cache['admin_intel']}\n\n"
        f"🤖 **AI Analysis:**\n{current_market_cache['ai_news']}\n\n"
        f"🕒 Sync: {current_market_cache['last_update']}\n\n"
        "⚠️ **အရောင်းအဝယ်မပြုလုပ်ပါ သတင်းအချက်အလက်တင်ပြခြင်းပါ**"
    )

# Command: /setmops 98.50 154.20 ဖြင့် တိုက်ရိုက်ဈေးပြောင်းရန်
@bot.message_handler(commands=['setmops'])
def handle_setmops(m):
    try:
        parts = m.text.split()
        if len(parts) >= 3:
            mogas_val = float(parts[1])
            diesel_val = float(parts[2])
            apply_mops_update(new_mogas=mogas_val, new_diesel=diesel_val)
            current_market_cache["last_mops_text"] = f"Updated via Admin Command: MOGAS ${mogas_val:.2f} \vert{} DIESEL${diesel_val:.2f}"
            bot.reply_to(m, f"✅ **MOPS ဈေးနှုန်းများ ပြောင်းလဲပြီးပါပြီ**\n• MOGAS: `${mogas_val:.2f}`\n• DIESEL: `${diesel_val:.2f}`", parse_mode="Markdown")
        else:
            bot.reply_to(m, "အသုံးပြုပုံ: `/setmops 98.50 154.20` (ပထမဂဏန်းသည် MOGAS၊ ဒုတိယဂဏန်းသည် DIESEL)", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(m, "⚠️ ဂဏန်းထည့်သွင်းမှု မှားယွင်းနေပါသည်။ ဥပမာ: `/setmops 98.50 154.20`")

@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    if m.text:
        text_lower = m.text.lower()
        # Group ထဲတွင် MOPS သတင်းစာသား ပို့ပါက ဂဏန်းများကို အလိုအလျောက် ဖမ်းယူပြီး Update လုပ်ပေးမည်
        if any(kw in text_lower for kw in ["mops", "mogas", "gasoil", "diesel", "singapore", "ဆီဈေး"]):
            current_market_cache["last_mops_text"] = m.text
            
            mogas_match = re.search(r'(?:mogas|92|95|n1b2)[^\d]*(\d{2,3}(?:\.\d+)?)', text_lower)
            diesel_match = re.search(r'(?:gasoil|diesel|10ppm|sgb1|sgb2)[^\d]*(\d{2,3}(?:\.\d+)?)', text_lower)
            
            m_val = float(mogas_match.group(1)) if mogas_match else None
            d_val = float(diesel_match.group(1)) if diesel_match else None
            
            if m_val or d_val:
                apply_mops_update(new_mogas=m_val, new_diesel=d_val)
                try:
                    bot.reply_to(m, f"🔄 MOPS ဈေးနှုန်းအသစ် မှတ်သားပြီးပါပြီ (MOGAS: {current_market_cache['mops_display']['MOGAS']}, DIESEL: {current_market_cache['mops_display']['GASOLINE']})")
                except: pass

        if "ဈေးနှုန်း" in m.text or "ဈေး" in m.text:
            try: bot.reply_to(m, generate_telegram_msg(), parse_mode="Markdown")
            except: pass

def dashboard_loop():
    while True:
        update_dashboard_data()
        time.sleep(300)

def telegram_loop():
    while True:
        update_dashboard_data()
        current_market_cache["ai_news"] = update_ai_analysis(current_market_cache["prices"])
        try: 
            bot.send_message(GROUP_CHAT_ID, generate_telegram_
