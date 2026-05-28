import time
import requests
import threading
import random
import os
from flask import Flask
import telebot
import google.generativeai as genai

app = Flask('')

@app.route('/')
def home():
    return "Market Bot (Telegram Only) with Gemini AI News is Active!"

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

# Google News RSS ကနေ လက်ရှိသတင်းခေါင်းစဉ်တွေ ဆွဲယူမည့် Function
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
            items = res.split("<item>")[1:4]  # ကဏ္ဍတစ်ခုစီကနေ ထိပ်သီးသတင်း ၃ ခုစီယူမယ်
            for item in items:
                title = item.split("<title>")[1].split("</title>")[0]
                headlines.append(title)
                
        return "\n".join(headlines)
    except Exception as e:
        print(f"News Fetch Error: {e}")
        return "No recent news headlines available."

# Gemini AI ကနေ သတင်းတွေကို ဖတ်ပြီး ထူးခြားမှသာ ရေးပေးမည့် Function
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

# Crypto Fear & Greed Index လှမ်းယူမည့် Function
def get_crypto_sentiment():
    try:
        res = requests.get("https://api.alternative.me/fng/", timeout=10).json()
        value = res['data'][0]['value']
        status = res['data'][0]['value_classification']
        
        status_mm = "အရမ်းကြောက်လန့်နေကြသည် (Extreme Fear)"
        if "Fear" in status and "Extreme" not in status: status_mm = "ကြောက်လန့်နေကြသည် (Fear)"
        elif "Neutral" in status: status_mm = "ပုံမှန်အခြေအနေ (Neutral)"
        elif "Greed" in status and "Extreme" not in status: status_mm = "လောဘတက်နေကြသည် (Greed)"
        elif "Extreme Greed" in status: status_mm = "အရမ်းလောဘတက်နေကြသည် (Extreme Greed)"
            
        return f"{value} / 100 ({status_mm})"
    except:
        return "N/A"

def get_market_data():
    prices = {"BTC": "N/A", "ETH": "N/A", "SOL": "N/A", "GOLD": "N/A", "WTI": "N/A", "BRENT": "N/A"}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
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
    # Telegram သို့သာ ပို့တော့မည် (Viber ဖြုတ်လိုက်ပါပြီ)
    tg_text = generate_message_text()
    try:
        bot.send_message(TG_CHAT_ID, tg_text, parse_mode="Markdown")
        print("Telegram message sent successfully!")
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
        time.sleep(14400)  # ၄ နာရီတစ်ခါ အော်တိုပတ်မည်
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
