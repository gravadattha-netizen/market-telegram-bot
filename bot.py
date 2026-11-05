import time
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

# Global Data Cache (ပုံပါ ဈေးနှုန်းအသစ်များဖြင့် အစပြုရန်)
current_market_cache = {
    "prices": {"WTI": 71.70, "BRENT": 76.00},
    "display_prices": {"WTI": "$71.70", "BRENT": "$76.00"},
    "trends": {"WTI": "up", "BRENT": "up"},
    
    # MOPS Data Cache (N1B2! = 100.44 နှင့် SGB2! = 157.34)
    "mops_prices": {"MOGAS": 100.44, "GASOLINE": 157.34},
    "mops_display": {"MOGAS": "$100.44", "GASOLINE": "$157.34"},
    "mops_signals": {"MOGAS": "SELL ▼", "GASOLINE": "SELL ▼"},

    "last_update": "N/A",
    "wti_gauge": 50,
    "brent_gauge": 55,
    "mogas_gauge": 40,
    "diesel_gauge": 35,
    "ai_news": "● ကမ္ဘာ့ရေနံဈေးကွက်သတင်းများကို AI ဖြင့် သေချာစွာ အနှစ်ချုပ် သုံးသပ်နေပါသည်...",
    "last_mops_text": "No custom MOPS news forwarded from group yet. Waiting for member updates...",
    "admin_intel": ADMIN_MESSAGE 
}

# ======= [ HTML UI - FIXED LAYOUT & GAUGES ] =======
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
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=500;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }
        body { background-color: #0b0f19; color: #f1f5f9; padding: 15px; }
        .container { max-width: 1200px; margin: 0 auto; width: 100%; }
        header { text-align: center; margin-bottom: 20px; border-bottom: 1px solid #1e293b; padding-bottom: 15px; }
        h1 { font-size: 1.5rem; color: #38bdf8; font-weight: 800; letter-spacing: 0.5px; }
        .greeting { color: #FFD700; font-size: 1rem; font-weight: bold; display: block; margin-top: 6px; }
        .sync-time { color: #64748b; font-size: 0.8rem; font-weight: bold; display: block; margin-top: 4px; }
        .section-title { font-size: 0.95rem; color: #38bdf8; font-weight: bold; text-align: center; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 0.5px; }
        .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 15px; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 15px; }
        .card { background: #111726; border-radius: 14px; border: 1px solid #1e293b; padding: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2); text-align: center; }
        .card-title { font-size: 0.85rem; color: #94a3b8; font-weight: bold; text-transform: uppercase; margin-bottom: 8px; }
        .price-val { font-size: 1.4rem; font-weight: 800; color: #ffffff; margin-bottom: 10px; }
        .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; }
        .badge-buy { background-color: #10b981; color: #ffffff; }
        .badge-sell { background-color: #ef4444; color: #ffffff; }
        .gauge-card { background: #111726; border-radius: 14px; padding: 12px; border: 1px solid #1e293b; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; overflow: hidden; }
        .gauge-header { font-size: 0.75rem; color: #94a3b8; font-weight: bold; margin-bottom: 8px; text-transform: uppercase; }
        .chart-container { width: 100%; height: 110px; display: flex; justify-content: center; align-items: center; overflow: hidden; }
        .ta-box { background: #111726; border: 1px solid #1e293b; border-radius: 14px; padding: 16px; margin-bottom: 15px; text-align: center; }
        .news-card-title { font-size: 0.85rem; color: #94a3b8; font-weight: bold; text-transform: uppercase; margin-bottom: 12px; border-bottom: 1px solid #1e293b; padding-bottom: 6px; text-align: left; }
        .news-box { line-height: 1.7; font-size: 0.9rem; color: #e2e8f0; white-space: pre-line; text-align: left; }
        footer { text-align: center; color: #ef4444; font-size: 0.8rem; font-weight: bold; padding: 12px; background: #070a12; border-radius: 12px; border: 1px solid rgba(239, 68, 68, 0.2); margin-top: 10px; }
        @media (max-width: 768px) {
            body { padding: 10px; }
            h1 { font-size: 1.3rem; }
            .grid-2 { grid-template-columns: 1fr; gap: 12px; }
            .grid-3 { grid-template-columns: 1fr; gap: 12px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Oil Energy Intelligence Hub Dashboard</h1>
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
                <div class="card-title">MOPS MOGAS</div>
                <div class="price-val" style="color: #38bdf8;">{{ data.mops_display.MOGAS }}</div>
                <div><span class="badge {{ 'badge-buy' if 'BUY' in data.mops_signals.MOGAS else 'badge-sell' }}">{{ data.mops_signals.MOGAS }}</span></div>
            </div>
            <div class="card">
                <div class="card-title">MOPS DIESEL 10PPM</div>
                <div class="price-val" style="color: #38bdf8;">{{ data.mops_display.GASOLINE }}</div>
                <div><span class="badge {{ 'badge-buy' if 'BUY' in data.mops_signals.GASOLINE else 'badge-sell' }}">{{ data.mops_signals.GASOLINE }}</span></div>
            </div>
        </div>

        <!-- 4 GAUGES SECTION (သပ်ရပ်စွာ နှစ်ကွက်စီ ခွဲထားသည်) -->
        <div class="section-title" style="margin-top: 20px;">📈 Market Sentiment Gauges</div>
        <div class="grid-2">
            <div class="gauge-card">
                <div class="gauge-header">🛢 WTI Crude</div>
                <div class="chart-container"><div id="wtiGauge"></div></div>
            </div>
            <div class="gauge-card">
                <div class="gauge-header">🔥 Brent Oil</div>
                <div class="chart-container"><div id="brentGauge"></div></div>
            </div>
        </div>
        <div class="grid-2">
            <div class="gauge-card">
                <div class="gauge-header">⛽ MOPS MOGAS</div>
                <div class="chart-container"><div id="mogasGauge"></div></div>
            </div>
            <div class="gauge-card">
                <div class="gauge-header">🚛 MOPS DIESEL</div>
                <div class="chart-container"><div id="dieselGauge"></div></div>
            </div>
        </div>

        <!-- TECHNICAL ANALYSIS SECTION -->
        <div class="ta-box">
            <div class="news-card-title" style="color: #fbbf24; text-align: center; border-bottom: none; margin-bottom: 8px;">
                📐 TECHNICAL ANALYSIS & INDICATORS SUMMARY
            </div>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 10px; margin-top: 10px;">
                <div><strong>MOGAS Signal:</strong> <span style="color: #38bdf8;">{{ data.mops_signals.MOGAS }}</span></div>
                <div><strong>DIESEL Signal:</strong> <span style="color: #38bdf8;">{{ data.mops_signals.GASOLINE }}</span></div>
                <div><strong>Summary Trend:</strong> <span style="color: #ef4444;">Bearish Momentum</span></div>
            </div>
        </div>

        <!-- Admin, AI & Member News -->
        <div class="grid-3" style="margin-top: 15px;">
            <div class="card" style="border: 1px solid rgba(255, 215, 0, 0.4); text-align: left;">
                <div class="news-card-title" style="color: #FFD700; border-bottom-color: rgba(255, 215, 0, 0.2);">✍️ ADMIN INTEL & OUTLOOK</div>
                <div class="news-box" style="color: #ffeaa7;">
                    {{ data.admin_intel }}
                </div>
            </div>

            <div class="card" style="text-align: left;">
                <div class="news-card-title" style="color: #60a5fa; border-bottom-color: #2e3d56;">🤖 OIL MARKET AI ANALYSIS</div>
                <div class="news-box">
                    {{ data.ai_news }}
                </div>
            </div>

            <div class="card" style="text-align: left;">
                <div class="news-card-title" style="color: #34d399; border-bottom-color: #2e3d56;">📢 MEMBER DAILY MOPS TRACKER</div>
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
            f"Prices: WTI={prices['WTI']}, Brent={prices['BRENT']}\n"
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

# ======= [ TRADINGVIEW DIRECT FETCH FOR EXACT PRICES ] =======
def fetch_tradingview_direct(symbol_full):
    try:
        url = "https://scanner.tradingview.com/cfd/scan"
        payload = {
            "symbols": {"tickers": [symbol_full]},
            "columns": ["close", "Recommend.All"]
        }
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.post(url, json=payload, headers=headers, timeout=10).json()
        
        if "data" in res and len(res["data"]) > 0:
            values = res["data"][0]["d"]
            close_price = round(float(values[0]), 2)
            rec = values[1]
            signal = "BUY ▲" if rec is not None and rec > 0 else "SELL ▼"
            gauge_val = 65 if rec is not None and rec > 0 else 35
            return close_price, signal, gauge_val
    except Exception as e:
        print(f"TradingView fetch error for {symbol_full}: {e}")
    return None, None, 40

def update_dashboard_data():
    prices = current_market_cache["prices"].copy()
    disp = current_market_cache["display_prices"].copy()
    trends = current_market_cache["trends"].copy()
    
    # 
