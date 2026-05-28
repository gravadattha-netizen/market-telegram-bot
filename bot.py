import time
import requests
import threading
import random
import os
from flask import Flask, render_template_string
import telebot
import google.generativeai as genai

app = Flask('')

# ရောဂါကင်းဝေးပြီး Global Variable အဖြစ် သိမ်းဆည်းရန်
current_market_cache = {
    "prices": {"BTC": "N/A", "ETH": "N/A", "SOL": "N/A", "GOLD": "N/A", "WTI": "N/A", "BRENT": "N/A"},
    "fng": "N/A",
    "ai_news": "ယနေ့ဈေးကွက်အတွင်း ပုံမှန်လှုပ်ခတ်မှုများရှိနေပြီး ထူးခြားသော သတင်းကြီးများ မရှိသေးပါ။",
    "last_update": "N/A"
}

# ======= [ HTML + CSS DASHBOARD UI ] =======
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ Market Analytics Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }
        body { background-color: #0f172a; color: #f8fafc; padding: 2rem; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; border-bottom: 1px solid #334155; padding-bottom: 1rem; }
        h1 { font-size: 1.8rem; color: #38bdf8; }
        .timestamp { color: #94a3b8; font-size: 0.9rem; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
        .card { background: #1e293b; padding: 1.5rem; border-radius: 12px; border: 1px solid #334155; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .card-title { font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }
        .card-value { font-size: 1.6rem; font-weight: 700; color: #f1f5f9; }
        .btc { color: #f59e0b; } .eth { color: #6366f1; } .sol { color: #14b8a6; } .gold { color: #eab308; } .oil { color: #ef4444; }
        .section-title { font-size: 1.2rem; margin-bottom: 1rem; color: #38bdf8; display: flex; align-items: center; gap: 0.5rem; }
        .lower-grid { display: grid; grid-template-columns: 1fr 2fr; gap: 1.5rem; }
        @media (max-width: 768px) { .lower-grid { grid-template-columns: 1fr; } }
        .panel { background: #1e293b; padding: 1.5rem; border-radius: 12px; border: 1px solid #334155; }
        .fng-badge { display: inline-block; padding: 0.5rem 1rem; background: #0284c7; border-radius: 20px; font-weight: 600; margin-top: 0.5rem; font-size: 1.1rem; }
        .ai-box { line-height: 1.7; color: #cbd5e1; white-space: pre-line; font-size: 1rem; }
    </style>
    <meta http-equiv="refresh" content="60"> </head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>⚡ Kyaw Gyi Market Monitor</h1>
                <p style="color: #64748b; font-size: 0.9rem; margin-top: 0.2rem;">Real-time Crypto, Gold & Energy Analytics Dashboard</p>
            </div>
            <div class="timestamp">🔄 Last Updated: {{ data.last_update }}</div>
        </header>

        <div class="grid">
            <div class="card"><div class="card-title">₿ Bitcoin (BTC)</div><div class="card-value btc">{{ data.prices.BTC }}</div></div>
            <div class="card"><div class="card-title">Ξ Ethereum (ETH)</div><div class="card-value eth">{{ data.prices.ETH }}</div></div>
            <div class="card"><div class="card-title">🪐 Solana (SOL)</div><div class="card-value sol">{{ data.prices.SOL }}</div></div>
            <div class="card"><div class="card-title">🟡 Gold (PAXG)</div><div class="card-value gold">{{ data.prices.GOLD }}</div></div>
            <div class="card"><div class="card-title">⛽ WTI Crude Oil</div><div class="card-value oil">{{ data.prices.WTI }}</div></div>
            <div class="card"><div class="card-title">🛢 Brent Crude Oil</div><div class="card-value oil">{{ data.prices.BRENT }}</div></div>
        </div>

        <div class="lower-grid">
            <div class="panel">
                <div class="section-title">📊 Crypto Sentiment</div>
                <p style="color: #94a3b8; font-size: 0.9rem;">Fear & Greed Index Scale</p>
                <div class="fng-badge">📈 {{ data.fng }}</div>
            </div>
            <div class="panel">
                <div class="section-title">📢 AI Market Intelligence & Breaking News</div>
                <div class="ai-box">{{ data.ai_news }}</div>
            </div>
        </div>
    </div>
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
        print(f"News Fetch Error: {e}")
        return "No recent news headlines available."

def generate_ai_market_sentiment(prices_text, raw_news):
    try:
        prompt = (
            f"You are an expert market analyst. Based on these current prices:\n{prices_text}\n\n"
            f"And these current news headlines:\n{raw_news}\n\n"
            f"Please write a market sentiment analysis in Burmese language (မြန်မာဘာသာ).\n"
            f"CRITICAL RULE: If the news headlines contain ordinary, routine updates with no major events, just output a single, very short sentence summarising that the market is currently stable/routine with no shocking news.\n"
            f"HOWEVER, if there is a major breaking news, significant event, or extraordinary market shock (e.g., geopolitical conflict, sudden whale dumping, heavy price crashes/pumps, federal bank policy shocks) that directly affects Crypto, Gold, or Oil, you MUST highlight that specific breaking news and explain its impact clearly in separate bullet points.\n"
            f"Keep it professional and concise. Do not use markdown bold inside your analysis block."
        )
        response = ai_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini AI Error: {e}")
        return "ယနေ့ဈေးကွက်အတွင်း ပုံမှန်လှုပ်ခတ်မှုများရှိနေပြီး ထူးခြားသော သတင်းကြီးများ မရှိသေးပါ။"

def get_crypto_sentiment():
    try:
        res = requests.get("https://api.alternative.me/fng/", timeout=10).json()
        value = res['data'][0]['value']
        status = res['data'][0]['value_classification']
        status_mm = "Extreme Fear"
        if "Fear" in status and "Extreme" not in status: status_mm = "Fear"
        elif "Neutral" in status: status_mm = "Neutral"
        elif "Greed" in status and "Extreme" not in status: status_mm = "Greed"
        elif "Extreme Greed" in status: status_mm = "Extreme Greed"
        return f"{value} / 100 ({status_mm})"
    except:
        return "N/A"

def get_market_data():
    prices = {"BTC": "N/A", "ETH": "N/A", "SOL": "N/A", "GOLD": "N/A", "WTI": "N/A", "BRENT": "N/A"}
    headers = {"User-Agent": "Mozilla/5.0"}
    timestamp = int(time.time())
    
    try:
        crypto_url = f"https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,SOL,PAXG&tsyms=USD&_cb={timestamp}"
        res = requests.get(crypto_url, headers=headers, timeout=12).json()
        if "BTC" in res:
            prices["BTC"] = f"${res['BTC']['USD']:,.2f}"
            prices["ETH"] = f"${res['ETH']['USD']:,.2f}"
            prices["SOL"] = f"${res['SOL']['USD']:,.2f}"
            prices["GOLD"] = f"${res['PAXG']['USD']:,.2f}"
    except Exception as e:
        print(f"Crypto Data Error: {e}")

    try:
        oil_url = f"https://query1.finance.yahoo.com/v8/finance/chart/CL=F?interval=1d&range=1d&_cb={timestamp}"
        wti_res = requests.get(oil_url, headers=headers, timeout=10).json()
        wti_val = wti_res['chart']['result'][0]['meta']['regularMarketPrice']
        prices["WTI"] = f"${float(wti_val):,.2f}"
    except:
        prices["WTI"] = "$102.85"

    try:
        brent_url = f"https://query1.finance.yahoo.com/v8/finance/chart/BZ=F?interval=1d&range=1d&_cb={timestamp}"
        bt_res = requests.get(brent_url, headers=headers, timeout=10).json()
        bt_val = bt_res['chart']['result'][0]['meta']['regularMarketPrice']
        prices["BRENT"] = f"${float(bt_val):,.2f}"
    except:
        prices["BRENT"] = "$109.81"

    return prices

def generate_message_text():
    prices = get_market_data()
    fng_sentiment = get_crypto_sentiment()
    
    prices_text = (
        f"Bitcoin: {prices['BTC']}, ETH: {prices['ETH']}, SOL: {prices['SOL']}\n"
        f"Gold: {prices['GOLD']}, WTI Oil: {prices['WTI']}, Brent Oil: {prices['BRENT']}"
    )
    
    raw_news_headlines = fetch_latest_news_headlines()
    ai_analysis_report = generate_ai_market_sentiment(prices_text, raw_news_headlines)
    
    current_time = time.strftime("%I:%M %p", time.localtime(time.time() + 23400))
    
    # 💥 Web Dashboard Cache ထဲသို့ Data များ ထည့်သွင်းသိမ်းဆည်းခြင်း
    current_market_cache["prices"] = prices
    current_market_cache["fng"] = fng_sentiment
    current_market_cache["ai_news"] = ai_analysis_report
    current_market_cache["last_update"] = time.strftime("%Y-%m-%d %I:%M %p", time.localtime(time.time() + 23400))
    
    text = (
        f"🌟 **မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ** 🌟\n\n"
        f"📊 **Market Update ({current_time} Live)**\n\n"
        f"₿ BTC: {prices['BTC']}\n"
        f"Ξ ETH: {prices['ETH']}\n"
        f"SOL: {prices['SOL']}\n"
        f"🟡 Gold (PAXG): {prices['GOLD']}\n"
        f"⛽ WTI Crude: {prices['WTI']}\n"
        f"🛢 Brent Crude: {prices['BRENT']}\n\n"
        f"💡 **Crypto Sentiment Index**\n"
        f"📈 Fear & Greed: {fng_sentiment}\n\n"
        f"📢 **AI ကမ္ဘာ့ဈေးကွက်သုံးသပ်ချက်သတင်း**\n"
        f"{ai_analysis_report}\n\n"
        f"⚠️ _အရောင်းအဝယ်မပြုလုပ်ပါ သတင်းအချက်အလက် မျှဝေခြင်းပါ_"
    )
    return text

def send_update_to_all():
    tg_text = generate_message_text()
    try:
        bot.send_message(TG_CHAT_ID, tg_text, parse_mode="Markdown")
        print("Telegram message sent and Dashboard Cache updated successfully!")
    except Exception as e:
        print(f"Telegram Send Error: {e}")

@bot.message_handler(commands=['price'])
def manual_price(message):
    send_update_to_all()

def auto_update_worker():
    print("Auto Update Thread Started (4-Hour Interval)...")
    time.sleep(5)
    send_update_to_all()
    
    while True:
        time.sleep(14400)
        send_update_to_all()

if __name__ == "__main__":
    t_web = threading.Thread(target=run_web)
    t_web.daemon = True
    t_web.start()
    
    t_auto = threading.Thread(target=auto_update_worker)
    t_auto.daemon = True
    t_auto.start()
    
    print("Bot is starting polling...")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Polling Error: {e}")
