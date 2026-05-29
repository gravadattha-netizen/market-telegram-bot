import time
import requests
import threading
import os
import re
from flask import Flask, render_template_string
import telebot
import google.generativeai as genai

app = Flask('')

current_market_cache = {
    "prices": {"BTC": 0, "ETH": 0, "SOL": 0, "GOLD": 0, "WTI": 0, "BRENT": 0},
    "display_prices": {"BTC": "0", "ETH": "0", "SOL": "0", "GOLD": "0", "WTI": "0", "BRENT": "0"},
    "fng": "50 Neutral",
    "ai_news": "စနစ်ကို စတင်နေပါသည်...",
    "member_news": "🚀 ဂရုထဲမှ မန်ဘာများ တင်ပေးမည့် ထူးခြားသတင်းများကို စောင့်ဆိုင်းနေပါသည်...",
    "last_update": "N/A",
    "crypto_gauge": 50,
    "wti_gauge": 50,
    "brent_gauge": 50,
    "gold_gauge": 50
}

# ======= [ HTML + APEXCHARTS GAUGE UI ] =======
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>🚀 Pro Market Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=600;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }
        body { background-color: #050a18; color: #e2e8f0; padding: 8px; overflow-x: hidden; }
        .container { max-width: 100%; margin: 0 auto; }
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid #1e293b; padding-bottom: 4px; }
        h1 { font-size: 0.95rem; background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
        .sync-time { color: #64748b; font-size: 0.6rem; font-weight: bold; }
        
        .top-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px; margin-bottom: 8px; }
        .stat-card { background: #0f172a; padding: 4px 2px; border-radius: 8px; border: 1px solid #1e293b; text-align: center; }
        .label { font-size: 0.55rem; color: #64748b; font-weight: 600; text-transform: uppercase; margin-bottom: 1px; }
        .val { font-size: 0.75rem; font-weight: 700; }
        
        .gauges-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; margin-bottom: 8px; }
        .gauge-panel { background: #0f172a; border-radius: 10px; padding: 6px 2px; border: 1px solid #1e293b; text-align: center; }
        .gauge-title { font-size: 0.65rem; color: #94a3b8; font-weight: 600; margin-bottom: 2px; }
        
        .panel { background: #0f172a; border-radius: 10px; padding: 8px; border: 1px solid #1e293b; margin-bottom: 6px; }
        .panel-title { font-size: 0.75rem; margin-bottom: 6px; color: #38bdf8; font-weight: 800; text-transform: uppercase; border-bottom: 1px dashed #1e293b; padding-bottom: 3px;}
        .ai-content { font-size: 0.68rem; line-height: 1.6; color: #cbd5e1; white-space: pre-line; }
        .member-content { font-size: 0.68rem; line-height: 1.6; color: #a7f3d0; white-space: pre-line; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div><h1>KYAW GYI ANALYTICS ⚡</h1></div>
            <div class="sync-time">{{ data.last_update }}</div>
        </header>

        <div class="top-row">
            <div class="stat-card"><div class="label">BTC</div><div class="val" style="color:#f59e0b">{{ data.display_prices.BTC.replace('$','').split('.')[0] }}</div></div>
            <div class="stat-card"><div class="label">ETH</div><div class="val" style="color:#6366f1">{{ data.display_prices.ETH.replace('$','').split('.')[0] }}</div></div>
            <div class="stat-card"><div class="label">SOL</div><div class="val" style="color:#14b8a6">{{ data.display_prices.SOL.replace('$','') }}</div></div>
            <div class="stat-card"><div class="label">GOLD</div><div class="val" style="color:#eab308">{{ data.display_prices.GOLD.replace('$','').split('.')[0] }}</div></div>
            <div class="stat-card"><div class="label">WTI</div><div class="val" style="color:#ef4444">{{ data.display_prices.WTI.replace('$','') }}</div></div>
            <div class="stat-card"><div class="label">BRENT</div><div class="val" style="color:#ff6b6b">{{ data.display_prices.BRENT.replace('$','') }}</div></div>
        </div>

        <div class="gauges-grid">
            <div class="gauge-panel">
                <div class="gauge-title">🪙 ခရစ်တို (F&G)</div>
                <div id="cryptoGauge"></div>
            </div>
            <div class="gauge-panel">
                <div class="gauge-title">🟡 ရွှေ (Spot Gold)</div>
                <div id="goldGauge"></div>
            </div>
            <div class="gauge-panel">
                <div class="gauge-title">🛢 WTI ရေနံ</div>
                <div id="wtiGauge"></div>
            </div>
            <div class="gauge-panel">
                <div class="gauge-title">🔥 BRENT ရေနံ</div>
                <div id="brentGauge"></div>
            </div>
        </div>

        <div class="panel" style="border-color: #059669; background: #022c22;">
            <div class="panel-title" style="color: #34d399;">🔥 Telegram Members Insights (ထူးခြားသတင်း)</div>
            <div class="member-content">{{ data.member_news }}</div>
        </div>

        <div class="panel">
            <div class="panel-title">📢 Global Market News & AI Deep Analysis</div>
            <div class="ai-content">{{ data.ai_news }}</div>
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
                        track: { background: '#1e293b', strokeWidth: '97%' },
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
        new ApexCharts(document.querySelector("#wtiGauge"), createGaugeOptions({{ data.wti_gauge }}, 'WTI Crude')).render();
        new ApexCharts(document.querySelector("#brentGauge"), createGaugeOptions({{ data.brent_gauge }}, 'Brent Crude')).render();
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

# ======= [ TELEGRAM & GEMINI CONFIG ] =======
TG_TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
bot = telebot.TeleBot(TG_TOKEN)

GENAI_API_KEY = "AIzaSyDE0tV" + "m05T8y6Yg8" + "fW96B6Y" + "W8C_S_G_V0"
genai.configure(api_key=GENAI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

# ======= [ GROUP MESSAGE HANDLER ] =======
@bot.message_handler(func=lambda message: True)
def handle_group_messages(message):
    user_text = message.text
    if not user_text:
        return

    sender_name = message.from_user.first_name if message.from_user.first_name else "Member"

    keywords = ["mops", "singapore", "10ppm", "92r", "95r", "97r", "price", "ဈေး", "/price", "သတင်း", "breaking", "news", "brent", "wti", "ရေနံ"]
    if any(kw in user_text.lower() for kw in keywords):
        try:
            if user_text.strip() == "/price":
                input_data = f"Current Prices:\n{str(current_market_cache['display_prices'])}\nFear & Greed: {current_market_cache['fng']}"
            else:
                input_data = user_text
                
                if user_text.strip() != "/price":
                    clean_text = user_text.replace('\n', ' ')
                    if len(clean_text) > 150:
                        clean_text = clean_text[:150] + "..."
                    current_market_cache["member_news"] = f"✍️ {sender_name}: {clean_text} ({time.strftime('%I:%M %p')})"

            prompt = (
                f"Analyze the following market/fuel data and write a response in Burmese language. "
                f"Be informative, highly engaging, and helpful for traders. Keep it under 4-5 sentences.\n\n"
                f"Data:\n{input_data}"
            )
            
            response = ai_model.generate_content(prompt)
            ai_reply = response.text
            
            bot.reply_to(message, f"📊 **Market Intelligence Update**\n\n{ai_reply}")
        except Exception as e:
            print(f"!!! GEMINI AI ERROR DETECTED: {e}")
            bot.reply_to(message, "⚠️ လက်ရှိတွင် ဈေးကွက်ဒေတာများကို ခွဲခြမ်းစိတ်ဖြာရန် အခက်အခဲရှိနေပါသည်။")

# ======= [ BACKGROUND DATA FETCHERS ] =======
def fetch_latest_news_headlines():
    try:
        urls = [
            "https://cointelegraph.com/rss/tag/bitcoin",
            "https://www.coindesk.com/arc/outboundfeed/rss/"
        ]
        headlines = []
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        for url in urls:
            res = requests.get(url, headers=headers, timeout=12).text
            titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', res)
            if not titles:
                titles = re.findall(r'<title>(.*?)</title>', res)
            for t in titles[1:4]:
                if "Cointelegraph" not in t and "CoinDesk" not in t:
                    headlines.append(t)
        if headlines:
            return "\n".join(headlines[:4])
        return "Global markets tracking stable. Crucial zones monitored."
    except Exception as e: 
        print(f"News Fetch Error: {e}")
        return "Routine global market updates sync active."

def generate_ai_market_sentiment(prices_text, raw_news):
    try:
        prompt = (
            f"Based on these current prices:\n{prices_text}\nAnd these global news headlines:\n{raw_news}\n"
            f"Please translate the core impact or write an analytical summary in Burmese language for a trading dashboard. "
            f"Make it informative, rich in content, and write around 3-4 sentences."
        )
        response = ai_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"AI Summary Error: {e}")
        return "ကမ္ဘာ့ဈေးကွက်သတင်းများကို လက်ရှိတွင် ဆွဲယူနေဆဲဖြစ်ပါသည်။ ဈေးနှုန်းဒေတာများအရ အပြောင်းအလဲ အနည်းငယ်ရှိနေပါသည်။"

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
    except: return 23, "23 Extreme Fear"

def update_all():
    prices, disp = get_market_data()
    fng_val, fng_lbl = get_fng_value()
    news_hd = fetch_latest_news_headlines()
    ai_rep = generate_ai_market_sentiment(str(disp), news_hd)
    
    current_market_cache["crypto_gauge"] = fng_val
    current_market_cache["wti_gauge"] = 45 if prices["WTI"] < 82 else 75
    current_market_cache["brent_gauge"] = 45 if prices["BRENT"] < 85 else 75
    current_market_cache["gold_gauge"] = 80
    
    current_market_cache["prices"] = prices
    current_market_cache["display_prices"] = disp
    current_market_cache["fng"] = fng_lbl
    current_market_cache["ai_news"] = ai_rep
    current_market_cache["last_update"] = time.strftime("%I:%M %p")

def auto_worker():
    time.sleep(2)
    update_all()
    while True:
        time.sleep(1800)
        update_all()

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    threading.Thread(target=auto_worker, daemon=True).start()
    
    # Conflict ရှင်းလင်းရန်အတွက် အဟောင်း Updates များကို ရှင်းထုတ်ပြီးမှ Poll လုပ်မည့် စနစ်
    try:
        bot.delete_webhook(drop_pending_updates=True)
        time.sleep(1)
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Polling Error: {e}")
