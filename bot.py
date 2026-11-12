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
TG_TOKEN = "8876036329:AAHSip397-NucbnJIX9aK9d2jeNo115gsX8" 
GROUP_CHAT_ID = -1003940722388  
GOOGLE_API_KEY = "AIzaSyAKM5IAugwBdKxrWQ__igkDwjwITW6f2kc"

genai.configure(api_key=GOOGLE_API_KEY)

# =========================================================
# ✍️ [ ADMIN INPUT ] - ဆီလုပ်ငန်းသတင်းများ ရေးထည့်ရန်နေရာ
# =========================================================
ADMIN_MESSAGE = """● QR စနစ်ဖြင့်တစ်နိုင်ငံလုံး ဆိုင်ပေါင်း ၁၉၂၇ ဆိုင်တပ်ဆင်ရောင်းချ ပေးနေပါသည်
● မန်ဘာများအားလုံး မိမိတို့ ပိုင်ဆိုင်မှုကို သေချာ စီမံခန့်ခွဲကြပါရန်။"""
# =========================================================

# Global Data Cache (ပုံပါ ဈေးနှုန်းအသစ်များဖြင့် အစပြုရန်)
current_market_cache = {
    "prices": {"WTI": 71.70, "BRENT": 76.00},
    "display_prices": {"WTI": "$71.70", "BRENT": "$76.00"},
    "trends": {"WTI": "up", "BRENT": "up"},
    
    # MOPS Data Cache (N1B2! = 101.54 နှင့် SGB2! = 154.98)
    "mops_prices": {"MOGAS": 101.54, "GASOLINE": 154.98},
    "mops_display": {"MOGAS": "$101.54", "GASOLINE": "$154.98"},
    "mops_signals": {"MOGAS": "BUY ▲", "GASOLINE": "BUY ▲"},
    "mops_ta": {"MOGAS": "STRONG BUY", "GASOLINE": "BUY"},

    "last_update": "N/A",
    "wti_gauge": 65,
    "brent_gauge": 68,
    "mogas_gauge": 70,
    "diesel_gauge": 65,
    "ai_news": "● ကမ္ဘာ့ရေနံဈေးကွက်သတင်းများကို AI ဖြင့် သေချာစွာ အနှစ်ချုပ် သုံးသပ်နေပါသည်...",
    "last_mops_text": "No custom MOPS news forwarded from group yet. Waiting for member updates...",
    "admin_intel": ADMIN_MESSAGE 
}

# ======= [ HTML UI - MODERN REDESIGNED DASHBOARD ] =======
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
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }
        body { background: linear-gradient(135deg, #070b14 0%, #0f172a 100%); color: #f8fafc; padding: 20px; min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; width: 100%; }
        
        header { text-align: center; margin-bottom: 25px; border-bottom: 1px solid rgba(56, 189, 248, 0.2); padding-bottom: 20px; background: rgba(17, 23, 38, 0.7); backdrop-filter: blur(10px); border-radius: 16px; padding: 20px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3); }
        h1 { font-size: 1.6rem; color: #38bdf8; font-weight: 800; letter-spacing: 0.8px; text-transform: uppercase; text-shadow: 0 2px 10px rgba(56,189,248,0.3); }
        .greeting { color: #fbbf24; font-size: 1rem; font-weight: 700; display: block; margin-top: 8px; }
        .sync-time { color: #94a3b8; font-size: 0.8rem; font-weight: 600; display: block; margin-top: 6px; }

        .section-title { font-size: 1rem; color: #38bdf8; font-weight: 800; text-align: center; margin: 20px 0 12px 0; text-transform: uppercase; letter-spacing: 1px; display: flex; align-items: center; justify-content: center; gap: 8px; }
        
        .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 15px; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 15px; }
        
        .card { background: rgba(17, 23, 38, 0.85); backdrop-filter: blur(12px); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08); padding: 18px; box-shadow: 0 8px 20px -4px rgba(0,0,0,0.4); text-align: center; transition: transform 0.2s ease, border-color 0.2s ease; }
        .card:hover { border-color: rgba(56, 189, 248, 0.4); transform: translateY(-2px); }
        .card-title { font-size: 0.85rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; margin-bottom: 10px; letter-spacing: 0.5px; }
        .price-val { font-size: 1.6rem; font-weight: 800; color: #ffffff; margin-bottom: 12px; text-shadow: 0 2px 8px rgba(0,0,0,0.5); }
        
        .badge { display: inline-block; padding: 6px 14px; border-radius: 30px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }
        .badge-buy { background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: #ffffff; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); }
        .badge-sell { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: #ffffff; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3); }

        .gauge-card { background: rgba(17, 23, 38, 0.8
