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
TG_TOKEN = "8876036329:AAHPL6sdZxUJUK0icXwMCS_VwboZPg6sI_w"
GROUP_CHAT_ID = -1003940722388
GOOGLE_API_KEY = "AIzaSyAKM5IAugwBdKxrWQ__igkDwjwITW6f2kc"

# ======= [ FACEBOOK PAGE AUTO POST CONFIG ] =======
FB_PAGE_ID = "61596981080298"
FB_PAGE_ACCESS_TOKEN = "YOUR_PAGE_ACCESS_TOKEN_HERE"

genai.configure(api_key=GOOGLE_API_KEY)

# =========================================================
# ✍️ [ ADMIN INPUT ] - ဆီလုပ်ငန်းသတင်းများ ရေးထည့်ရန်နေရာ
# =========================================================
ADMIN_MESSAGE = """● QR စနစ်ဖြင့်တစ်နိုင်ငံလုံး ဆိုင်ပေါင်း ၁၉၂၇ ဆိုင်တပ်ဆင်ရောင်းချ ပေးနေပါသည်
● မန်ဘာများအားလုံး မိမိတို့ ပိုင်ဆိုင်မှုကို သေချာ စီမံခန့်ခွဲကြပါရန်။"""

# =========================================================
# 💵 [ MANUAL MOPS INPUT ] - N1B2 (MOGAS) နှင့် SGB2 (DIESEL) ဈေးထည့်ရန်
# ဂဏန်းများကို $(  ) ထဲတွင် Manual ထည့်သွင်းပါ (ဥပမာ - 97.24, 153.30)
# =========================================================
MOPS_N1B2_PRICE = $(  )  # N1B2 (MOGAS) ဈေးနှုန်း ထည့်ရန်
MOPS_SGB2_PRICE = $(  )  # SGB2 (DIESEL) ဈေးနှုန်း ထည့်ရန်
# =========================================================

# Global Data Cache
current_market_cache = {
    "prices": {"WTI": 71.70, "BRENT": 76.00},
    "display_prices": {"WTI": "$71.70", "BRENT": "$76.00"},
    "trends": {"WTI": "up", "BRENT": "up"},

    # MOPS Data Cache (Manual ထည့်သွင်းထားသော ဈေးနှုန်းများဖြင့် အစပြုရန်)
    "mops_prices": {"MOGAS": MOPS_N1B2_PRICE, "GASOLINE": MOPS_SGB2_PRICE},
    "mops_display": {"MOGAS": f"${MOPS_N1B2_PRICE}", "GASOLINE": f"${MOPS_SGB2_PRICE}"},
    "mops_signals": {"MOGAS": "SELL ▼", "GASOLINE": "BUY ▲"},

    "last_update": "N/A",
    "wti_gauge": 50,
    "brent_gauge": 55,
    "mogas_gauge": 40,
    "diesel_gauge": 65,
    "ai_news": "● ကမ္ဘာ့ရေနံဈေးကွက်သတင်းများကို AI ဖြင့် သေချာစွာ အနှစ်ချုပ် သုံးသပ်နေပါသည်...",
    "last_mops_text": "No custom MOPS news forwarded from group yet. Waiting for member updates...",
    "admin_intel": ADMIN_MESSAGE
}

# ======= [ HTML UI - FIXED GAUGES & EXACT PRICES ] =======
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
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800&display=swap" rel="stylesheet">
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
        .news-box { line-height: 1.7; font-size: 0.9rem; color: #e2e8f0; white
