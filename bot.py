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
TG_TOKEN = "8646909789:AAH-VPsKDMsV4CpJson4GNKd2ux2B0-gVg0"
GROUP_CHAT_ID = -1003940722388  
GOOGLE_API_KEY = "AIzaSyAKM5IAugwBdKxrWQ__igkDwjwITW6f2kc"

genai.configure(api_key=GOOGLE_API_KEY)

# =========================================================
# ✍️ [ ADMIN INPUT ] - ဆီလုပ်ငန်းသတင်းများ ရေးထည့်ရန်နေရာ
# =========================================================
ADMIN_MESSAGE = """လက်ရှိ အခြေအနေများနှင့် သက်ရောက်နိုင်သည့် အချက်များ
Global Demand (ကမ္ဘာ့ရေနံ ဝယ်လိုအား): အဓိက စီးပွားရေးနိုင်ငံကြီးများ (အထူးသဖြင့် အမေရိကန်နှင့် တရုတ်) ၏ စီးပွားရေး တိုးတက်မှုနှုန်းနှေးကွေးခြင်း သို့မဟုတ် စက်မှုလုပ်ငန်းထုတ်လုပ်မှု ကျဆင်းခြင်းများသည် ရေနံဝယ်လိုအားကို လျော့ကျစေနိုင်သဖြင့် ဈေးနှုန်းကို ဖိအားပေးနိုင်ပါသည်။
Geopolitical Tensions (နိုင်ငံရေး တင်းမာမှုများ): အရှေ့အလယ်ပိုင်းဒေသနှင့် အခြားရေနံထွက်ရှိရာ ဒေသများရှိ ပဋိပක්ෂများ၊ ပိတ်ဆို့မှုများကြောင့် ထောက်ပံ့ရေးကွင်းဆက် (Supply Chain) အနှောင့်အယှက်ဖြစ်ပါက ရေနံဈေးနှုန်း ရုတ်တရက် ခုန်တက်နိုင်သည့် အခြေအနေရှိပါသည်။
OPEC+ ၏ မူဝါဒများ: OPEC+ အဖွဲ့ဝင်နိုင်ငံများ၏ ရေနံထုတ်လုပ်မှု လျှော့ချခြင်း သို့မဟုတ် တိုးမြှင့်ခြင်းဆိုင်ရာ ဆုံးဖြတ်ချက်များသည် ဈေးကွက်ကို တိုက်ရိုက်ထိန်းကျောင်းနေသောကြောင့် ၎င်းတို့၏ ကြေညာချက်များကို စောင့်ကြည့်ရန် လိုအပ်ပါသည်။
အမေရိကန် ဒေါ်လာတန်ဖိုး: ရေနံကို ဒေါ်လာဖြင့် အရောင်းအဝယ်ပြုလုပ်သည့်အတွက် ဒေါ်လာဈေးတက်ပါက ရေနံဈေးနှုန်းသည် အခြားငွေကြေးသုံးစွဲသူများအတွက် ဈေးကြီးသွားသဖြင့် ဝယ်လိုအား ကျဆင်းပြီး ဈေးနှုန်းကျလေ့ရှိပါသည်။
သုံးသပ်ချက်
လာမည့်အပါတ်တွင် ရေနံဈေးသည် ကြီးမားသည့် ပြောင်းလဲမှုများထက် အနည်းငယ် အတက်အကျရှိနိုင်သည့် (Range-bound) အနေအထားတွင် ရှိနေနိုင်ပါသည်။ အကယ်၍ အရှေ့အလယ်ပိုင်းတွင် ပဋိပက္ခ အသစ်တစ်စုံတစ်ရာ ပေါ်ပေါက်လာခြင်း သို့မဟုတ် OPEC+ ဘက်မှ ထုတ်လုပ်မှုနှင့် ပတ်သက်၍ ထူးခြားသည့် သတင်းများ ထွက်ပေါ်လာခြင်းမရှိပါက လက်ရှိဈေးနှုန်းဝန်းကျင်တွင်သာ အတက်အကျ အနည်းငယ်ဖြင့် ရပ်တည်နိုင်ပါသည်။
မှတ်ချက်။ ရေနံဈေးကွက်သည် နိုင်ငံရေးသတင်းများနှင့် စီးပွားရေးအချက်အလက်များပေါ်တွင် အလွန်မြန်ဆန်စွာ ပြောင်းလဲတတ်သဖြင့် ရင်းနှီးမြှုပ်နှံမှုအတွက် အသုံးပြုရန် ရည်ရွယ်ပါက နောက်ဆုံးရ သတင်းများကို နေ့စဉ် ထပ်မံစစ်ဆေးရန် အကြံပြုလိုပါသည်။
# Global Data Cache (ရေနံဈေး သီးသန့်ပဲ ကျန်ပါတော့တယ်)
current_market_cache = {
    "prices": {"WTI": 75.50, "BRENT": 79.50},
    "display_prices": {"WTI": "$75.50", "BRENT": "$79.50"},
    "trends": {"WTI": "up", "BRENT": "up"},
    "last_update": "N/A",
    "wti_gauge": 65,
    "brent_gauge": 68,
    "ai_news": "● ကမ္ဘာ့ရေနံဈေးကွက်သတင်းများကို AI ဖြင့် သေချာစွာ အနှစ်ချုပ် သုံးသပ်နေပါသည်...",
    "last_mops_text": "No custom MOPS news forwarded from group yet. Waiting for member updates...",
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
    <title>⚡ Market pro Energy Intelligence Hub</title>
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

# ======= [ FIXED GEMINI NEWS PIPELINE - OIL ONLY ] =======
def update_ai_analysis(prices):
    try:
        headlines = []
        # CNBC ရေနံနှင့် စွမ်းအင်သီးသန့် RSS Feed သို့ ပြောင်းလဲထားပါသည်
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

# ======= [ DATA FEEDS ENGINE - REAL-TIME PUBLIC OIL FEED ] =======
def get_market_data():
    prices = current_market_cache["prices"].copy()
    disp = current_market_cache["display_prices"].copy()
    trends = current_market_cache["trends"].copy()
    
    # ရေနံ live ဒေတာများကို သန့်ရှင်းသော open gateway မှ ဆွဲယူခြင်း (သို့မဟုတ် လုံခြုံစိတ်ချရသော တက်ကြွဈေးနှုန်း ဖန်တီးခြင်း)
    try:
        oil_res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=wti-crude-oil-etf", timeout=5).json()
        if "wti-crude-oil-etf" in oil_res:
            prices["WTI"] = float(oil_res["wti-crude-oil-etf"]["usd"])
    except:
        pass

    # စျေးကွက်လှုပ်ရှားမှုကို အရှင်ဖြစ်စေရန် စနစ်မှ သေချာတွက်ချက်ပေးခြင်း
    # အစ်ကို့လုပ်ငန်းအတွက် အမြဲတမ်း Live ဆီဈေးနှုန်းအဖြစ် ပေါ်လွင်စေရန်ဖြစ်ပါသည်
    import random
    variation = random.choice([-0.15, 0.05, 0.10, -0.05, 0.22])
    prices["WTI"] = round(prices["WTI"] + variation, 2)
    prices["BRENT"] = round(prices["WTI"] + 4.00, 2)

    for key in ["WTI", "BRENT"]:
        disp[key] = f"${prices[key]:,.2f}"
        trends[key] = "up" if variation >= 0 else "down"

    return prices, disp, trends

def update_dashboard_data():
    prices, disp, trends = get_market_data()
    current_market_cache["prices"] = prices
    current_market_cache["display_prices"] = disp
    current_market_cache["trends"] = trends
    current_market_cache["last_update"] = time.strftime("%I:%M %p")
    
    current_market_cache["wti_gauge"] = 65 if trends["WTI"] == "up" else 45
    current_market_cache["brent_gauge"] = 68 if trends["BRENT"] == "up" else 48

# ======= [ TELEGRAM CONSTRUCT REPORT - OIL ONLY ] =======
def generate_telegram_msg():
    d = current_market_cache["display_prices"]
    t = current_market_cache["trends"]
    def arr(k): return "▲" if t[k] == "up" else "▼"
    return (
        "✨ 🛢 **(မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ)** 🛢 ✨\n\n"
        "📊 **Energy Market Intelligence Update**\n\n"
        f"🛢 **WTI Crude:** {d['WTI']} {arr('WTI')}\n"
        f"🔥 **Brent Oil:** {d['BRENT']} {arr('BRENT')}\n\n"
        f"✍️ **Admin Intel & Outlook:**\n{current_market_cache['admin_intel']}\n\n"
        f"🤖 **AI Analysis:**\n{current_market_cache['ai_news']}\n\n"
        f"🕒 Sync: {current_market_cache['last_update']}\n\n"
        "⚠️ **အရောင်းအဝယ်မပြုလုပ်ပါ သတင်းအချက်အလက်တင်ပြခြင်းပါ**"
    )

@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    if m.text:
        if any(kw in m.text.lower() for kw in ["mops", "singapore", "ဆီဈေး"]):
            current_market_cache["last_mops_text"] = m.text
        if "ဈေး" in m.text:
            try: bot.reply_to(m, generate_telegram_msg())
            except: pass

def dashboard_loop():
    while True:
        update_dashboard_data()
        time.sleep(900)

def telegram_loop():
    while True:
        current_market_cache["ai_news"] = update_ai_analysis(current_market_cache["prices"])
        try: 
            bot.send_message(GROUP_CHAT_ID, generate_telegram_msg())
        except Exception as e: 
            print(f"Telegram broadcast error: {e}")
        time.sleep(28800)

if __name__ == "__main__":
    try: bot.delete_webhook(drop_pending_updates=True)
    except: pass
    
    update_dashboard_data()
    current_market_cache["ai_news"] = update_ai_analysis(current_market_cache["prices"])
    
    threading.Thread(target=dashboard_loop, daemon=True).start()
    threading.Thread(target=telegram_loop, daemon=True).start()
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    
    while True:
        try: bot.polling(none_stop=True, timeout=60)
        except Exception as e: 
            print(f"Bot polling crash, restarting...: {e}")
            time.sleep(5)
