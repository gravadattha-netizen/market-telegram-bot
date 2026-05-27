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
    return "Market Bot (Telegram + Viber) with Gemini AI News is Active!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ======= [ 1. TELEGRAM CONFIG ] =======
TG_TOKEN = "8646909789:AAHfAkmDGPgO1unJdxMl4EavLBDXM8V2mkc"
TG_CHAT_ID = "-1003940722388"
bot = telebot.TeleBot(TG_TOKEN)

# ======= [ 2. VIBER CONFIG ] =======
VIBER_TOKEN = "515a44391e843e1d-c6a85536be62b3df-ef03348c4de8da51"
VIBER_CHAT_ID = "gM7EonpInpS+560GZ/258w=="

# ======= [ 3. GEMINI AI CONFIG ] =======
# ကျော်ကြီးရဲ့ Gemini API Key ကို ဒီနေရာမှာ ထည့်ပေးပါ
GENAI_API_KEY = "AIzaSyAKM5IAugwBdKxrWQ__igkDwjwITW6f2kc"
genai.configure(api_key=GENAI_API_KEY)
ai_model = genai.GenerativeModel('gemini-pro')

# Google News RSS ကနေ လက်ရှိသတင်းခေါင်းစဉ်တွေ ဆွဲယူမည့် Function
def fetch_latest_news_headlines():
    try:
        # Crypto, Gold, Oil သတင်းခေါင်းစဉ်များကို စုစည်းယူခြင်း
        urls = [
            "https://news.google.com/rss/search?q=crypto+bitcoin&hl=en-US&gl=US&ceid=US:en",
            "https://news.google.com/rss/search?q=crude+oil+wti+brent&hl=en-US&gl=US&ceid=US:en",
            "https://news.google.com/rss/search?q=gold+market+price&hl=en-US&gl=US&ceid=US:en"
        ]
        headlines = []
        headers = {"User-Agent": "Mozilla/5.0"}
        
        for url in urls:
            res = requests.get(url, headers=headers, timeout=10).text
            # RSS xml ထဲက <title> ခေါင်းစဉ်များကို သန့်စင်ပြီး ဆွဲထုတ်ခြင်း
            items = res.split("<item>")[1:4]  # တစ်ခုချင်းစီကနေ ထိပ်သီးသတင်း ၃ ခုစီယူမယ်
            for item in items:
                title = item.split("<title>")[1].split("</title>")[0]
                headlines.append(title)
                
        return "\n".join(headlines)
    except Exception as e:
        print(f"News Fetch Error: {e}")
        return "No recent news headlines available."

# Gemini AI ကနေ သတင်းတွေကို ဖတ်ပြီး မြန်မာလို အနှစ်ချုပ် သုံးသပ်ပေးမည့် Function
def generate_ai_market_sentiment(prices_text, raw_news):
    try:
        prompt = (
            f"You are an expert market analyst. Based on these current prices:\n{prices_text}\n\n"
            f"And these current news headlines:\n{raw_news}\n\n"
            f"Please write a comprehensive market sentiment analysis in Burmese language (မြန်မာဘာသာ). "
            f"Include separate short analysis points for Crypto/Bitcoin, Gold, and Crude Oil (WTI/Brent) explaining why prices might be changing. "
            f"Keep it professional, informative, easy to read, and formatted with clean bullet points. "
            f"Do not use markdown bold inside your analysis block, just use plain Burmese text with spacing."
        )
        response = ai_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini AI Error: {e}")
        return "ယနေ့ဈေးကွက်အတွင်း ပုံမှန်လှုပ်ခတ်မှုများရှိနေပြီး သတင်းအချက်အလက်များကို ဆက်လက်စောင့်ကြည့်ရန် လိုအပ်ပါသည်။"

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

def generate_message_text(is_viber=False):
    prices = get_market_data()
    fng_sentiment = get_crypto_sentiment()
    
    # ဈေးနှုန်းဒေတာများကို စာသားအဖြစ်ပြောင်းလဲခြင်း
    prices_text = (
        f"Bitcoin: {prices['BTC']}, ETH: {prices['ETH']}, SOL: {prices['SOL']}\n"
        f"Gold: {prices['GOLD']}, WTI Oil: {prices['WTI']}, Brent Oil: {prices['BRENT']}"
    )
    
    # သတင်းများကို Live ဆွဲယူပြီး Gemini ခိုင်းခြင်း
    raw_news_headlines = fetch_latest_news_headlines()
    ai_analysis_report = generate_ai_market_sentiment(prices_text, raw_news_headlines)
    
    b = "*" if is_viber else "**"
    current_time = time.strftime("%I:%M %p", time.localtime(time.time() + 23400))
    
    text = (
        f"🌟 {b}မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ{b} 🌟\n\n"
        f"📊 {b}Market Update ({current_time} Live){b}\n\n"
        f"₿ BTC: {prices['BTC']}\n"
        f"Ξ ETH: {prices['ETH']}\n"
        f"SOL: {prices['SOL']}\n"
        f"🟡 Gold (PAXG): {prices['GOLD']}\n"
        f"⛽ WTI Crude: {prices['WTI']}\n"
        f"🛢 Brent Crude: {prices['BRENT']}\n\n"
        f"💡 {b}Crypto Sentiment Index{b}\n"
        f"📈 Fear & Greed: {fng_sentiment}\n\n"
        f"📢 {b}AI ကမ္ဘာ့ဈေးကွက်သုံးသပ်ချက်သတင်း{b}\n"
        f"{ai_analysis_report}\n\n"
        f"⚠️ _အရောင်းအဝယ်မပြုလုပ်ပါ သတင်းအချက်အလက် မျှဝေခြင်းပါ_"
    )
    return text

def send_update_to_all():
    # ၁။ Telegram သို့ ပို့ခြင်း
    tg_text = generate_message_text(is_viber=False)
    try:
        bot.send_message(TG_CHAT_ID, tg_text, parse_mode="Markdown")
        print("Telegram message sent successfully!")
    except Exception as e:
        print(f"Telegram Send Error: {e}")

    # ၂။ Viber သို့ ပို့ခြင်း
    viber_text = generate_message_text(is_viber=True)
    viber_url = "https://chatapi.viber.com/pa/send_message"
    viber_headers = {"X-Viber-Auth-Token": VIBER_TOKEN}
    viber_payload = {
        "chat_id": VIBER_CHAT_ID,
        "min_api_version": 1,
        "sender": {"name": "Market Live Report"},
        "type": "text",
        "text": viber_text
    }
    try:
        res = requests.post(viber_url, json=viber_payload, headers=viber_headers, timeout=10)
        print(f"Viber response: {res.status_code}")
    except Exception as e:
        print(f"Viber Send Error: {e}")

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
