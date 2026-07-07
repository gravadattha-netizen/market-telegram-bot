import os
import requests
import json
from datetime import datetime
from openai import OpenAI

# Configuration (ထည့်သွင်းပြီးသား အချက်အလက်များ)
TELEGRAM_BOT_TOKEN = "8646909789:AAFhLamWEWkqjnCd2pfjEXn5lMoBWPCejNo"
TELEGRAM_CHAT_ID = "-1003940722388"
OPENAI_API_KEY = "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"

# 1. Binance API ဆီကနေ ဈေးနှုန်း Data ဆွဲယူခြင်း
def get_binance_prices():
    prices = {}
    
    # Spot Prices (BTC, ETH)
    spot_symbols = ["BTCUSDT", "ETHUSDT"]
    for sym in spot_symbols:
        try:
            res = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={sym}").json()
            prices[sym] = {
                "lastPrice": float(res["lastPrice"]),
                "priceChangePercent": float(res["priceChangePercent"])
            }
        except Exception as e:
            print(f"Error fetching {sym}: {e}")
        
    # Futures Prices (Crude Oil, Gold, Brent)
    futures_symbols = ["CLUSDT", "XAUUSDT", "BZUSDT"]
    for sym in futures_symbols:
        try:
            res = requests.get(f"https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={sym}").json()
            prices[sym] = {
                "lastPrice": float(res["lastPrice"]),
                "priceChangePercent": float(res["priceChangePercent"])
            }
        except Exception as e:
            print(f"Error fetching {sym}: {e}")
        
    return prices

# 2. OpenAI သုံးပြီး သတင်းစာသားနှင့် ပုံ ဖန်တီးခြင်း
def generate_report_and_image(prices):
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # HTML Table သို့မဟုတ် JSON Data ပုံစံ ပြင်ဆင်ခြင်း
    data_str = json.dumps(prices, indent=2)
    
    prompt = f"""
    သင်သည် ကျွမ်းကျင်သော စီးပွားရေးသတင်းထောက်တစ်ယောက် ဖြစ်သည်။ သင့်အလုပ်မှာ ပေးထားသော Data ကို သတင်းဆောင်းပါးအဖြစ် ပြောင်းလဲပေးရန် ဖြစ်သည်။
    စာရင်း (List) များ လုံးဝမသုံးရ။ ပေးထားသော အခေါ်အဝေါ်များကိုသာ တိကျစွာ သုံးပါ။
    
    အောက်ပါ data ကိုအသုံးပြု၍ စီးပွားရေးသတင်းဆောင်းပါးတစ်ပုဒ်ကို မြန်မာဘာသာဖြင့် ရေးပါ။ အပိုဒ် (၃) ပိုဒ်သာ ရေးပါ။
    သတင်း ခေါင်းစဉ် ကို ဈေးကွက် အခြေအနေအတိုင်း ရေးသားပေးပါ။ (ဥပမာ- # သတင်းခေါင်းစဉ် ဈေးကွက်အတွင်း အကျဘက်ဦးတည်နေသည့် ရင်းနှီးမြှုပ်နှံမှုပစ္စည်းများ)
    
    ဈေးနှုန်းများ တက်ပါက (Bold) စာလုံးအထူ ပြုလုပ်ပေးပြီး၊ ကျပါက (Italic) စာလုံးစောင်း ပြုလုပ်ပေးပါ။ HTML tags များ လုံးဝမသုံးရပါ။
    
    Data: {data_str}
    """
    
    # AI သတင်းဆောင်းပါး ရေးသားခြင်း
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    report_text = completion.choices[0].message.content
    
    # AI ဖြင့် ပုံဖော်ခြင်း (DALL-E)
    print("DALL-E ဖြင့် သတင်းဓာတ်ပုံ ဖန်တီးနေပါသည်...")
    image_response = client.images.generate(
        model="dall-e-3",
        prompt="A professional financial and cryptocurrency market trend background chart, corporate and clean dark-blue tech style, no text inside image.",
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = image_response.data[0].url
    
    return report_text, image_url

# 3. Telegram သို့ စာနှင့် ပုံ တွဲပြီး ပို့ခြင်း
def send_to_telegram(text, image_url):
    photo_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "photo": image_url,
        "caption": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(photo_url, json=payload)
    return response.json()

# အဓိက Run မည့် နေရာ
if __name__ == "__main__":
    print("၁။ Binance API ထံမှ နောက်ဆုံးရဈေးနှုန်းများ ဆွဲယူနေပါသည်...")
    market_data = get_binance_prices()
    print("ရရှိလာသော Data:", market_data)
    
    print("\n၂။ OpenAI GPT ဖြင့် မြန်မာလို သတင်းဆောင်းပါး ရေးသားနေပါသည်...")
    report, img_url = generate_report_and_image(market_data)
    
    print("\n၃။ Telegram Channel သို့ ပုံနှင့်စာ ပို့ဆောင်နေပါသည်...")
    result = send_to_telegram(report, img_url)
    
    if result.get("ok"):
        print("\n✨ အောင်မြင်စွာ ပို့ဆောင်ပြီးပါပြီဗျာ!")
    else:
        print("\n❌ Telegram သို့ ပို့ရာတွင် အမှားအယွင်းရှိပါသည်:", result)
