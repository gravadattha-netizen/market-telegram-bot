import time
import requests
import threading
import os
from flask import Flask, render_template_string
import telebot
import google.generativeai as genai

app = Flask('')

# ဒေတာများကို Analytics အတွက် သိမ်းဆည်းရန်
current_market_cache = {
    "prices": {"BTC": 0, "ETH": 0, "SOL": 0, "GOLD": 0, "WTI": 0, "BRENT": 0},
    "display_prices": {"BTC": "0", "ETH": "0", "SOL": "0", "GOLD": "0", "WTI": "0", "BRENT": "0"},
    "fng": "N/A",
    "ai_news": "စနစ်ကို စတင်နေပါသည်...",
    "last_update": "N/A"
}

# ======= [ HTML + CHART.JS DASHBOARD UI ] =======
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Pro Market Analytics</title>
    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }
        body { background-color: #050a18; color: #e2e8f0; padding: 1.5rem; }
        .container { max-width: 1300px; margin: 0 auto; }
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
        h1 { font-size: 1.6rem; background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
        
        .top-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .stat-card { background: #0f172a; padding: 1.2rem; border-radius: 16px; border: 1px solid #1e293b; transition: 0.3s; }
        .stat-card:hover { border-color: #38bdf8; transform: translateY(-3px); }
        .label { font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem; }
        .val { font-size: 1.4rem; font-weight: 700; }
        
        .charts-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem; }
        @media (max-width: 900px) { .charts-grid { grid-template-columns: 1fr; } }
        
        .panel { background: #0f172a; border-radius: 20px; padding: 1.5rem; border: 1px solid #1e293b; }
        .panel-title { font-size: 1rem; margin-bottom: 1.2rem; color: #94a3b8; font-weight: 600; display: flex; align-items: center; gap: 0.5rem; }
        
        .ai-content { font-size: 0.95rem; line-height: 1.8; color: #cbd5e1; white-space: pre-line; }
        .fng-meter { text-align: center; padding: 1rem; border-radius: 12px; background: #1e293b; font-weight: 700; color: #38bdf8; font-size: 1.2rem; }
    </style>
    <meta http-equiv="refresh" content="60">
</head>
<body>
    <div class="container">
        <header>
            <div><h1>KYAW GYI ANALYTICS ⚡</h1><p style="color: #64748b; font-size: 0.8rem;">Intelligence-Driven Market Monitoring</p></div>
            <div style="text-align: right;"><p style="color: #64748b; font-size: 0.8rem;">Last Sync</p><p style="font-weight: 600;">{{ data.last_update }}</p></div>
        </header>

        <div class="top-row">
            <div class="stat-card"><div class="label">BTC/USD</div><div class="val" style="color:#f59e0b">{{ data.display_prices.BTC }}</div></div>
            <div class="stat-card"><div class="label">ETH/USD</div><div class="val" style="color:#6366f1">{{ data.display_prices.ETH }}</div></div>
            <div class="stat-card"><div class="label">SOL/USD</div><div class="val" style="color:#14b8a6">{{ data.display_prices.SOL }}</div></div>
            <div class="stat-card"><div class="label">Gold Oz</div><div class="val" style="color:#eab308">{{ data.display_prices.GOLD }}</div></div>
            <div class="stat-card"><div class="label">Oil Brent</div><div class="val" style="color:#ef4444">{{ data.display_prices.BRENT }}</div></div>
        </div>

        <div class="charts-grid">
            <div class="panel">
                <div class="panel-title">📈 Asset Performance Comparison</div>
                <div id="performanceChart"></div>
            </div>
            <div class="panel">
                <div class="panel-title">📊 Market Sentiment</div>
                <div class="fng-meter">{{ data.fng }}</div>
                <div id="gaugeChart" style="margin-top:1rem;"></div>
            </div>
        </div>

        <div class="panel">
            <div class="panel-title">📢 AI Deep Analysis & Market Insights</div>
            <div class="ai-content">{{ data.ai_news }}</div>
        </div>
    </div>

    <script>
        // Data Performance Chart
        var options = {
            series: [{
                name: 'Price Value',
                data: [{{ data.prices.BTC }}, {{ data.prices.ETH }}, {{ data.prices.SOL }}, {{ data.prices.GOLD }}]
            }],
            chart: { type: 'bar', height: 300, toolbar: {show: false}, fontFamily: 'Plus Jakarta Sans' },
            colors: ['#38bdf8'],
            plotOptions: { bar: { borderRadius: 8, columnWidth: '40%', } },
            xaxis: { categories: ['BTC', 'ETH', 'SOL', 'GOLD'], labels: {style: {colors: '#64748b'}} },
            theme: { mode: 'dark' },
            grid: { borderColor: '#1e293b' }
        };
        new ApexCharts(document.querySelector("#performanceChart"), options).render();

        // Gauge Chart for Sentiment
        var gaugeOptions = {
            series: [{{ data.fng.split(' ')[0] }}],
            chart: { height: 250, type: 'radialBar', },
            plotOptions: {
                radialBar: {
                    hollow: { size: '70%', },
                    dataLabels: { name: {show: false}, value: { color: '#38bdf8', fontSize: '30px', fontWeight: 700, show: true } }
                }
            },
            colors: ['#38bdf8'],
            labels: ['Sentiment'],
        };
        new ApexCharts(document.querySelector("#gaugeChart"), gaugeOptions).render();
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

# ======= [ 1. TELEGRAM CONFIG ] =======
TG_TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
TG_CHAT_ID = "-1003940722388"
bot = telebot.TeleBot(TG_TOKEN)

# ======= [ 2. GEMINI AI CONFIG ] =======
GENAI_API_KEY = "AIzaSyAKM5IAugwBdKxrWQ__igkDwjwITW6f2kc"
genai.configure(api_key=GENAI_API_KEY)
ai_model = genai.GenerativeModel('gemini-pro')

def fetch_latest_news_headlines():
    try:
        urls = [
            "https://news.google.com/rss/search?q=crypto+bitcoin&hl=en-US&gl=US&ceid=US:en",
            "https://news.google.com/rss/search?q=crude+oil+wti+brent&hl=en-US&gl=US&ceid=US:en",
            "https://news.google.com/rss/search?q=gold+market+price&hl=en-US&gl=US&ceid=US:en"
        ]
        headlines = []
        headers = {"User-Agent": "Mozilla/5.0"}
        for url in urls:
            res = requests.get(url, headers=headers, timeout=10).text
            items = res.split("<item>")[1:4]
            for item in items:
                title = item.split("<title>")[1].split("</title>")[0]
                headlines.append(title)
        return "\n".join(headlines)
    except Exception as e:
        return "Routine market data sync."

def generate_ai_market_sentiment(prices_text, raw_news):
    try:
        prompt = (
            f"Current prices:\n{prices_text}\nNews:\n{raw_news}\n"
            f"Write a brief market analysis in Burmese. Be professional. Concise."
        )
        response = ai_model.generate_content(prompt)
        return response.text
    except:
        return "ဈေးကွက်ပုံမှန်အတိုင်းရှိနေပါသည်။"

def get_market_data():
    prices = {"BTC": 0, "ETH": 0, "SOL": 0, "GOLD": 0, "WTI": 0, "BRENT": 0}
    disp = {"BTC": "0", "ETH": "0", "SOL": "0", "GOLD": "0", "WTI": "0", "BRENT": "0"}
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        crypto_url = f"https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,SOL,PAXG&tsyms=USD"
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
        oil_url = f"https://query1.finance.yahoo.com/v8/finance/chart/BZ=F?interval=1d&range=1d"
        bt_res = requests.get(oil_url, headers=headers, timeout=10).json()
        prices["BRENT"] = bt_res['chart']['result'][0]['meta']['regularMarketPrice']
        disp["BRENT"] = f"${float(prices['BRENT']):,.2f}"
    except: disp["BRENT"] = "$0.00"

    return prices, disp

def get_fng():
    try:
        res = requests.get("https://api.alternative.me/fng/").json()
        return f"{res['data'][0]['value']} {res['data'][0]['value_classification']}"
    except: return "50 Neutral"

def update_all():
    prices, disp = get_market_data()
    fng = get_fng()
    news_hd = fetch_latest_news_headlines()
    ai_rep = generate_ai_market_sentiment(str(disp), news_hd)
    
    current_market_cache["prices"] = prices
    current_market_cache["display_prices"] = disp
    current_market_cache["fng"] = fng
    current_market_cache["ai_news"] = ai_rep
    current_market_cache["last_update"] = time.strftime("%Y-%m-%d %I:%M %p")
    
    msg = f"📊 **Market Update**\n\nBTC: {disp['BTC']}\nETH: {disp['ETH']}\nGOLD: {disp['GOLD']}\nOIL: {disp['BRENT']}\n\n💡 **AI Analysis**\n{ai_rep}"
    try: bot.send_message(TG_CHAT_ID, msg, parse_mode="Markdown")
    except: pass

def auto_worker():
    while True:
        update_all()
        time.sleep(14400)

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    auto_worker()
