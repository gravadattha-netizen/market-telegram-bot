import os
import time
import requests
import threading
import xml.etree.ElementTree as ET
from flask import Flask, render_template_string
import telebot
import google.generativeai as genai

app = Flask('')

# ======= [ CONFIGURATION - TOKENS & KEYS ] =======
TG_TOKEN = os.environ.get("TG_TOKEN", "8646909789:AAH6uYspvEsKAQX__ZlthAOPEr-Dv6__ORg")
GROUP_CHAT_ID = int(os.environ.get("GROUP_CHAT_ID", -1003940722388))
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "AIzaSyAKM5IAugwBdKxrWQ__igkDwjwITW6f2kc")

genai.configure(api_key=GOOGLE_API_KEY)

# ======= [ MOPS DATA PERSISTENCE (FILE SAVING) ] =======
def save_mops_to_file(text):
    """ MOPS စာသားအသစ်ဝင်လာပါက mops_data.txt ထဲသို့ ရေးသိမ်းမည် """
    try:
        with open("mops_data.txt", "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        print(f"Error saving MOPS file: {e}")

def load_mops_from_file():
    """ Server ပြန်ပွင့်လာပါက mops_data.txt ဖိုင်ထဲမှ စာအဟောင်းကို ပြန်ဖတ်မည် """
    if os.path.exists("mops_data.txt"):
        try:
            with open("mops_data.txt", "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return content
        except Exception as e:
            print(f"Error reading MOPS file: {e}")
    return "No custom MOPS news forwarded from group yet. Waiting for member updates..."

# =========================================================
# ✍️ [ ADMIN INPUT ] - ဆီလုပ်ငန်းသတင်းများ ရေးထည့်ရန်နေရာ
# =========================================================
ADMIN_MESSAGE = """Crude Oil WTI ရဲ့ ၄ နာရီပြဇယား (4-Hour Chart) သုံးသပ်ချက်ကို မြန်မာလို အနှစ်ချုပ် ရှင်းပြပေးထားပါတယ်။
📊 ၄ နာရီပြဇယား (4H Chart) ရဲ့ လက်ရှိအခြေအနေ
လက်ရှိမှာ Crude Oil ဈေးနှုန်းဟာ $76.80 – $77.20 ကြားမှာ ကျဉ်းမြောင်းစွာ ငြိမ်နေပြီး ခန်းမှန်းရခက်သည့် အခြေအနေ (Consolidation) မှာ ရောက်ရှိနေပါတယ်။ ဒါဟာ မကြာမီ ဈေးနှုန်း သိသိသာသာ လှုပ်ရှားတော့မယ့် အရိပ်အယောင် ဖြစ်ပါတယ်။
 * အနီးကပ် လားရာ (Intraday Trend): အနည်းငယ် အကျဘက် ဦးတည်နေသော်လည်း $76.00 – $76.20 ဝန်းကျင်မှာ အောက်ခြေ ထောက်ခံမှု ရှိနေပါတယ်။
 * 4H Moving Averages: ဈေးနှုန်းဟာ 20-period EMA ($77.15) အနီးမှာ လှည့်ပတ်နေပြီး၊ 50-period EMA ဖြစ်တဲ့ $77.85 က အထက်ဘက်မှာ ခုခံအဆင့်အဖြစ် တားဆီးထားပါတယ်။
 * Momentum (RSI): RSI က 44 – 48 ကြားမှာ ရှိနေတာကြောင့် ဝယ်သူနဲ့ ရောင်းသူ အင်အား မျှမျှတတ ရှိနေကြောင်း ပြသနေပါတယ်။
🎯 သတိပြုရမည့် အရေးကြီး အဆင့်များ (Key Levels)
၁။ အထက်ဘက် ခုခံအဆင့်များ (Resistance)
 * $77.50 – $77.80: 4H 20/50 EMA နဲ့ VWAP တို့ ဆုံသည့်နေရာ ဖြစ်ပါတယ်။ 4H candle တစ်ခုဟာ $77.85 အထက်မှာ ပိတ်နိုင်မှသာ ကျဆင်းမှုကို ရပ်တန့်ပြီး $79.20 ဘက်သို့ ဆက်လက် တက်လှမ်းနိုင်ပါမယ်။
 * $79.20 – $79.80: အဓိက အရောင်းအဝယ် ထူထပ်သည့် ဇုန် (Major Supply Zone) ဖြစ်လို့ ဒီနေရာရောက်ရင် အကျဘက် ပြန်ကွေ့နိုင်ခြေ ရှိပါတယ်။
၂။ အောက်ဘက် ပံ့ပိုးအဆင့်များ (Support)
 * $76.40 – $76.00: Daily 200 SMA ရဲ့ အဓိက ခံစစ်စည်း ဖြစ်ပါတယ်။
 * $74.80 – $74.20: $76.00 ထက် အောက်ကို ကျဆင်းသွားပါက ဒုတိယမြောက် ရောက်ရှိနိုင်သည့် ပံ့ပိုးဇုန် (Demand Zone) ဖြစ်ပါတယ်။
⚡ အရောင်းအဝယ်ပြုလုပ်နိုင်သည့် နည်းလမ်းများ (Trade Scenarios)
🟢 အတက်ဘက် အရောင်းအဝယ် (Bullish Setup)
 * ဝင်ရောက်ရမည့်အချက် (Trigger): 4H Candle သည် $77.85 အထက်တွင် အားကောင်းစွာ ပိတ်နိုင်လျှင်။
 * ပစ်မှတ် (Targets): $79.20 / $80.50
 * အရှုံးဖြတ်ရန် (Stop Loss): $76.80 အောက်
🔴 အကျဘက် အရောင်းအဝယ် (Bearish Setup)
 * ဝင်ရောက်ရမည့်အချက် (Trigger): 4H Candle သည် $76.00 အောက်သို့ လျှောကျ ပိတ်နိုင်လျှင်။
 * ပစ်မှတ် (Targets): $74.80 / $73.50
 * အရှုံးဖြတ်ရန် (Stop Loss): $77.10 အထက်
💡 အဓိက အကြံပြုချက်
 * $76.00 မှ $77.85 ကြား သည် ဈေးငြိမ်နေသည့် ဘောင်အတွင်း ရောက်ရှိနေသဖြင့် ကြားထဲတွင် အလောတကြီး ဝင်ရောက် အရောင်းအဝယ် မလုပ်ဘဲ အထက် သို့မဟုတ် အောက် ဘက်သို့ အတည်ပြု ခွဲထွက်ချိန် (Breakout) မှသာ ဝင်ရောက်ခြင်းက အန္တရာယ် ကင်းဆုံး ဖြစ်ပါမည်။

● မန်ဘာများအားလုံး မိမိတို့ ပိုင်ဆိုင်မှုကို သေချာ စီမံခန့်ခွဲကြပါရန်။"""

# Global Data Cache
current_market_cache = {
    "prices": {"WTI": 71.70, "BRENT": 76.00},
    "display_prices": {"WTI": "$71.70", "BRENT": "$76.00"},
    "trends": {"WTI": "up", "BRENT": "up"},
    "last_update": "N/A",
    "wti_gauge": 50,
    "brent_gauge": 55,
    "ai_news": "● ကမ္ဘာ့ရေနံဈေးကွက်သတင်းများကို AI ဖြင့် သေချာစွာ အနှစ်ချုပ် သုံးသပ်နေပါသည်...",
    "last_mops_text": load_mops_from_file(),  # ဖိုင်ထဲမှ စာအဟောင်းကို အလိုအလျောက် ပြန်ဆွဲယူမည်
    "admin_intel": ADMIN_MESSAGE 
}

# ======= [ HTML UI - OIL PORTAL ONLY ] =======
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
        .grid-1 { display: grid; grid-template-columns: 1fr; gap: 15px; margin-bottom: 15px; }
        .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 15px; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 15px; }
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
        .news-box { line-height: 1.7; font-size: 0.9rem; color: #e2e8f0; white-space: pre-line; text-align: left; }
        footer { text-align: center; color: #ef4444; font-size: 0.8rem; font-weight: bold; padding: 12px; background: #070a12; border-radius: 12px; border: 1px solid rgba(239, 68, 68, 0.2); margin-top: 10px; }
        @media (max-width: 768px) {
            body { padding: 10px; }
            h1 { font-size: 1.3rem; }
            .grid-2 { grid-template-columns: 1fr; gap: 12px; }
            .grid-3 { grid-template-columns: 1fr; gap: 12px; }
            .card { padding: 12px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>KYAW GYI ENERGY INTELLIGENCE HUB ⚡</h1>
            <span class="greeting">(မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ)</span>
            <span class="sync-time">Last Sync: {{ data.last_update }}</span>
        </header>

        <div class="grid-1">
            <div class="card">
                <div class="card-title">🛢 INTERNATIONAL ENERGIES (ကမ္ဘာ့ရေနံဈေးနှုန်းများ)</div>
                <div class="row-item">
                    <span class="label-text">WTI Crude Oil</span>
                    <span class="val-text {{ data.trends.WTI }}">{{ data.display_prices.WTI }}</span>
                </div>
                <div class="row-item">
                    <span class="label-text">Brent Crude Oil</span>
                    <span class="val-text {{ data.trends.BRENT }}">{{ data.display_prices.BRENT }}</span>
                </div>
            </div>
        </div>

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

        <div class="grid-3">
            <div class="card" style="border: 1px solid rgba(255, 215, 0, 0.4);">
                <div class="card-title" style="color: #FFD700; border-bottom-color: rgba(255, 215, 0, 0.2);">✍️ ADMIN INTEL & OIL OUTLOOK</div>
                <div class="news-box" style="color: #ffeaa7;">
                    {{ data.admin_intel }}
                </div>
            </div>

            <div class="card">
                <div class="card-title" style="color: #60a5fa; border-bottom-color: #2e3d56;">🤖 OIL MARKET AI AUTOMATED ANALYSIS</div>
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
        rss_url = "https://www.cnbc.com/id/19832390/device/rss/rss.html"
        res = requests.get(rss_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        if res.status_code == 200:
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
        if response and response.text and len(response.text.strip()) > 10:
            return response.text.strip()
    except Exception as e:
        print(f"Gemini error: {e}")
    return "● ကမ္ဘာ့ရေနံဈေးကွက်သည် လက်ရှိအခြေအနေတွင် ပုံမှန်အတိုင်း ဆက်လက်ရွေ့လျားနေပါသည်။\n● နိုင်ငံတကာစွမ်းအင်လိုအပ်ချက်နှင့် ထုတ်လုပ်မှုအခြေအနေများကို စောင့်ကြည့်ရပါမည်။"

# ======= [ YAHOO FINANCE FIXED LIVE FEED ] =======
def fetch_yahoo_oil_price(symbol):
    endpoints = [
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d",
        f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
    ]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    for url in endpoints:
        try:
            response = requests.get(url, headers=headers, timeout=7).json()
            meta = response['chart']['result'][0]['meta']
            price = meta['regularMarketPrice']
            prev_close = meta.get('previousClose', price)
            trend = "up" if price >= prev_close else "down"
            return round(float(price), 2), trend
        except Exception:
            continue
            
    print(f"Yahoo Finance fetch error for {symbol}")
    return None, None

def update_dashboard_data():
    prices = current_market_cache["prices"].copy()
    disp = current_market_cache["display_prices"].copy()
    trends = current_market_cache["trends"].copy()
    
    # 1. WTI Crude Oil Live (CL=F)
    wti_p, wti_t = fetch_yahoo_oil_price("CL=F")
    if wti_p:
        prices["WTI"] = wti_p
        trends["WTI"] = wti_t
        
    # 2. Brent Crude Oil Live (BZ=F)
    brent_p, brent_t = fetch_yahoo_oil_price("BZ=F")
    if brent_p:
        prices["BRENT"] = brent_p
        trends["BRENT"] = brent_t
    else:
        prices["BRENT"] = round(prices["WTI"] + 4.10, 2)
        trends["BRENT"] = trends["WTI"]

    for key in ["WTI", "BRENT"]:
        disp[key] = f"${prices[key]:,.2f}"

    current_market_cache["prices"] = prices
    current_market_cache["display_prices"] = disp
    current_market_cache["trends"] = trends
    
    # မြန်မာစံတော်ချိန် (+6:30)
    current_market_cache["last_update"] = time.strftime("%I:%M %p", time.localtime(time.time() + 23400))
    
    current_market_cache["wti_gauge"] = 65 if trends["WTI"] == "up" else 45
    current_market_cache["brent_gauge"] = 68 if trends["BRENT"] == "up" else 48

# ======= [ TELEGRAM CONSTRUCT REPORT (HTML FORMAT) ] =======
def generate_telegram_msg():
    d = current_market_cache["display_prices"]
    t = current_market_cache["trends"]
    def arr(k): return "▲" if t[k] == "up" else "▼"
    return (
        "✨ 🛢 <b>(မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ)</b> 🛢 ✨\n\n"
        "📊 <b>Energy Market Intelligence Update</b>\n\n"
        f"🛢 <b>WTI Crude:</b> <code>{d['WTI']}</code> {arr('WTI')}\n"
        f"🔥 <b>Brent Oil:</b> <code>{d['BRENT']}</code> {arr('BRENT')}\n\n"
        f"✍️ <b>Admin Intel & Outlook:</b>\n{current_market_cache['admin_intel']}\n\n"
        f"🤖 <b>AI Analysis:</b>\n{current_market_cache['ai_news']}\n\n"
        f"🕒 Sync: {current_market_cache['last_update']}\n\n"
        "⚠️ <b>အရောင်းအဝယ်မပြုလုပ်ပါ သတင်းအချက်အလက်တင်ပြခြင်းပါ</b>"
    )

@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    if m.text:
        # MOPS, Singapore သို့မဟုတ် ဆီဈေး ပါသော စာကို ဖမ်းယူပြီး memory နှင့် file ထဲ သိမ်းဆည်းခြင်း
        if any(kw in m.text.lower() for kw in ["mops", "singapore", "ဆီဈေး"]):
            current_market_cache["last_mops_text"] = m.text
            save_mops_to_file(m.text)
            
        if "ဈေး" in m.text:
            try: 
                bot.reply_to(m, generate_telegram_msg(), parse_mode="HTML")
            except Exception as e:
                print(f"Reply error: {e}")

def dashboard_loop():
    while True:
        update_dashboard_data()
        time.sleep(300)

def telegram_loop():
    while True:
        update_dashboard_data()
        current_market_cache["ai_news"] = update_ai_analysis(current_market_cache["prices"])
        try: 
            bot.send_message(GROUP_CHAT_ID, generate_telegram_msg(), parse_mode="HTML")
        except Exception as e: 
            print(f"Telegram broadcast error: {e}")
        time.sleep(28800)

if __name__ == "__main__":
    try: 
        bot.delete_webhook(drop_pending_updates=True)
    except: 
        pass
    
    update_dashboard_data()
    current_market_cache["ai_news"] = update_ai_analysis(current_market_cache["prices"])
    
    threading.Thread(target=dashboard_loop, daemon=True).start()
    threading.Thread(target=telegram_loop, daemon=True).start()
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    
    while True:
        try: 
            bot.polling(none_stop=True, timeout=60)
        except Exception as e: 
            print(f"Bot polling crash, restarting...: {e}")
            time.sleep(5)
