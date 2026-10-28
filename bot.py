import threading
import os
import xml.etree.ElementTree as ET
from flask import Flask, render_template_string
import telebot
import google.generativeai as genai

app = Flask(__name__)

# ======= [ CONFIGURATION - TOKENS & KEYS ] =======
TG_TOKEN = "8646909789:AAEHviwhSkNKyMAw6jTIGz_O2jxxE8SafvY"
GROUP_CHAT_ID = "-1003940722388"
GOOGLE_API_KEY = "AIzaSyAKM5IAugwBdKxrWQ__igkDwjwITW6f2kc"

genai.configure(api_key=GOOGLE_API_KEY)

# ======= [ ADMIN CUSTOM INPUT ] =======
#လာမည့် သောကြာနေ့ 30.10.2026 PPRD ဈေး HSD/PD အနေဖြင့် 100 ကျပ်ခန့် တက်နိုင် ပြီး ပေါက်စုံ ဈေး 92/95 မှာ ဈေးအနည်းငယ် ကျနိုင် ပါသည်\n• QR စနစ်ဖြင့်တစ်နိုင်ငံလုံး ဆိုင်ပေါင်း ၁၇၃၀ တပ်ဆင်ရောင်းချပေးနေပါသည်\
ADMIN_MESSAGE = "• QR စနစ်ဖြင့်တစ်နိုင်ငံလုံး ဆိုင်ပေါင်း ၁၇၃၀ တပ်ဆင်ရောင်းချပေးနေပါသည်\n• မန်ဘာများအားလုံး မိမိတို့ ပိုင်ဆိုင်မှုကို သေချာ စီမံခန့်ခွဲကြပါရန့်။"

# Global Data Cache (Dashboard အတွက်)
current_market_cache = {
    "prices": {"WTI": "71.70", "BRENT": "76.00"},
    "display_prices": {"WTI": "$71.70", "BRENT": "$76.00"},
    "trends": {"WTI": "up", "BRENT": "up"},
    "ai_analysis": "ဈေးကွက်အခြေအနေကို ဆန်းစစ်နေပါသည်။",
    "admin_intel": ADMIN_MESSAGE
}

bot = telebot.TeleBot(TG_TOKEN)

def fetch_oil_prices():
    # ရေနံဈေးနှုန်း ရယူရန် function
    try:
        return {"WTI": "101.41", "BRENT": "110.89"}, {"WTI": "$101.41", "BRENT": "$110.89"}, {"WTI": "up", "BRENT": "up"}
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return current_market_cache["prices"], current_market_cache["display_prices"], current_market_cache["trends"]

def generate_ai_analysis():
    # AI မှ ကမ္ဘာ့အရေးအခင်း၊ စစ်ရေး၊ နိုင်ငံရေးနှင့် ရေနံဈေးသုံးသပ်ချက်ကို အလိုအလျောက် ရေးသားခြင်း
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            "ကမ္ဘာ့အရေးအခင်း၊ စစ်ရေး၊ နိုင်ငံရေးနှင့် ရေနံစွမ်းအင်ဈေးကွက်အခြေအနေများကို မြန်မာဘာသာဖြင့် "
            "အချက် ၁ချက် သို့မဟုတ် ၂ချက်ပါဝင်သော တိုတိုရှင်းရှင်းနှင့် ထိမိသော Market Analysis အဖြစ် ရေးသားပေးပါ။ "
            "bullet points (•) ဖြင့် ဖော်ပြပေးပါ။"
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"AI Error: {e}")
        return "• ကမ္ဘာ့ရေနံဈေးကွက်သည် လက်ရှိအခြေအနေတွင် ပုံမှန်အတိုင်း ဆက်လက်ရွေ့လျားနေပါသည်။\n• နိုင်ငံတကာစွမ်းအင်လိုအပ်ချက်နှင့် ထုတ်လုပ်မှုအခြေအနေများကို စောင့်ကြည့်ရပါမည်။"

@app.route("/")
def dashboard():
    # Dashboard တွင် Group မှ Data များကို ဆွဲယူပြသရန်
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Oil Energy Intelligence Hub Dashboard</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; background-color: #121212; color: #e0e0e0; padding: 20px; }
            .container { max-width: 800px; margin: auto; background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
            h1 { color: #ffa726; text-align: center; }
            .card { background: #2d2d2d; padding: 15px; margin-bottom: 15px; border-radius: 5px; }
            .price { font-size: 20px; color: #66bb6a; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Oil Energy Intelligence Hub Dashboard</h1>
            <div class="card">
                <h3>Live Prices</h3>
                <p class="price">WTI Crude: {{ prices.WTI }} | Brent Oil: {{ prices.BRENT }}</p>
            </div>
            <div class="card">
                <h3>Admin Intel & Outlook</h3>
                <p>{{ admin_intel }}</p>
            </div>
            <div class="card">
                <h3>AI Analysis</h3>
                <p>{{ ai_analysis }}</p>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(
        html_template,
        prices=current_market_cache["display_prices"],
        admin_intel=current_market_cache["admin_intel"],
        ai_analysis=current_market_cache["ai_analysis"]
    )

def send_telegram_update():
    try:
        prices, display_prices, trends = fetch_oil_prices()
        ai_text = generate_ai_analysis()
        
        current_market_cache["prices"] = prices
        current_market_cache["display_prices"] = display_prices
        current_market_cache["trends"] = trends
        current_market_cache["ai_analysis"] = ai_text
        current_market_cache["admin_intel"] = ADMIN_MESSAGE

        wti_arrow = "▲" if trends["WTI"] == "up" else "▼"
        brent_arrow = "▲" if trends["BRENT"] == "up" else "▼"

        message = (
            "✨ 🛢 **(မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ)** 🛢 ✨\n\n"
            "📊 **Energy Market Intelligence Update**\n\n"
            f"🛢 **WTI Crude:** {display_prices['WTI']} {wti_arrow}\n"
            f"🔥 **Brent Oil:** {display_prices['BRENT']} {brent_arrow}\n\n"
            "✍️ **Admin Intel & Outlook:**\n"
            f"{ADMIN_MESSAGE}\n\n"
            "🤖 **AI Analysis:**\n"
            f"{ai_text}\n\n"
            "🕒 Sync: 05:12 AM\n\n"
            "⚠️ **အရောင်းအဝယ်မပြုလုပ်ပါ သတင်းအချက်အလက်တင်ပြခြင်းပါ**"
        )

        bot.send_message(GROUP_CHAT_ID, message, parse_mode="Markdown")
        print("Telegram update sent successfully!")
    except Exception as e:
        print(f"Error sending telegram message: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
