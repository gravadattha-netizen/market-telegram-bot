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
ADMIN_MESSAGE = """● QR စနစ်ဖြင့်တစ်နိုင်ငံလုံး ဆိုင်ပေါင်း ၁၉၂၇ ဆိုင်တပ်ဆင်ရောင်းချ ပေးနေပါသည် လာမည့် အပတ် PPRD ဈေး ကျပါမည်
● မန်ဘာများအားလုံး မိမိတို့ ပိုင်ဆိုင်မှုကို သေချာ စီမံခန့်ခွဲကြပါရန်။"""
# =========================================================

# Global Data Cache (ပုံပါ ဈေးနှုန်းအသစ်များဖြင့် အစပြုရန်)
current_market_cache = {
    "prices": {"WTI": 71.70, "BRENT": 76.00},
    "display_prices": {"WTI": "$71.70", "BRENT": "$76.00"},
    "trends": {"WTI": "up", "BRENT": "up"},
    
    # MOPS Data Cache (N1B2! = 100.08 နှင့် SGB2! = 149.38)
    "mops_prices": {"MOGAS": 100.08, "GASOLINE": 149.38},
    "mops_display": {"MOGAS": "$100.08", "GASOLINE": "$149.38"},
    "mops_signals": {"MOGAS": "SELL ▼", "GASOLINE": "SELL ▼"},

    "last_update": "N/A",
    "wti_gauge": 50,
    "brent_gauge": 55,
    "mogas_gauge": 40,
    "diesel_gauge": 35,
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
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=500;700;800&display=swap" rel="stylesheet">
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
        .news-box { line-height: 1.7; font-size: 0.9rem; color: #e2e8f0; white-space: pre-line; text-align: left; }
        footer { text-align: center; color: #ef4444; font-size: 0.8rem; font-weight: bold; padding: 12px; background: #070a12; border-radius: 12px; border: 1px solid rgba(239, 68, 68, 0.2); margin-top: 10px; }
        @media (max-width: 768px) {
            body { padding: 10px; }
            h1 { font-size: 1.3rem; }
            .grid-2 { grid-template-columns: 1fr; gap: 12px; }
            .grid-3 { grid-template-columns: 1fr; gap: 12px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Oil Energy Intelligence Hub Dashboard</h1>
            <span class="greeting">(မင်္ဂလာရှိသောနေ့လေးဖြစ်ပါစေ)</span>
            <span class="sync-time">Last Sync: {{ data.last_update }}</span>
        </header>

        <div class="section-title">📊 Live Market Prices & MOPS Update</div>
        
        <!-- Live Prices Cards -->
        <div class="grid-2">
            <div class="card">
                <div class="card-title">WTI Crude</div>
                <div class="price-val">{{ data.display_prices.WTI }}</div>
                <div><span class="badge {{ 'badge-buy' if data.trends.WTI == 'up' else 'badge-sell' }}">{{ 'BUY ▲' if data.trends.WTI == 'up' else 'SELL ▼' }}</span></div>
            </div>
            <div class="card">
                <div class="card-title">Brent Oil</div>
                <div class="price-val">{{ data.display_prices.BRENT }}</div>
                <div><span class="badge {{ 'badge-buy' if data.trends.BRENT == 'up' else 'badge-sell' }}">{{ 'BUY ▲' if data.trends.BRENT == 'up' else 'SELL ▼' }}</span></div>
            </div>
        </div>

        <div class="grid-2">
            <div class="card">
                <div class="card-title">MOPS MOGAS</div>
                <div class="price-val" style="color: #38bdf8;">{{ data.mops_display.MOGAS }}</div>
                <div><span class="badge {{ 'badge-buy' if 'BUY' in data.mops_signals.MOGAS else 'badge-sell' }}">{{ data.mops_signals.MOGAS }}</span></div>
            </div>
            <div class="card">
                <div class="card-title">MOPS DIESEL 10PPM</div>
                <div class="price-val" style="color: #38bdf8;">{{ data.mops_display.GASOLINE }}</div>
                <div><span class="badge {{ 'badge-buy' if 'BUY' in data.mops_signals.GASOLINE else 'badge-sell' }}">{{ data.mops_signals.GASOLINE }}</span></div>
            </div>
        </div>

        <!-- 4 GAUGES SECTION -->
        <div class="section-title" style="margin-top: 20px;">📈 Market Sentiment Gauges</div>
        <div class="grid-2">
            <div class="gauge-card">
                <div class="gauge-header">🛢 WTI Crude</div>
                <div class="chart-container"><div id="wtiGauge"></div></div>
            </div>
            <div class="gauge-card">
                <div class="gauge-header">🔥 Brent Oil</div>
                <div class="chart-container"><div id="brentGauge"></div></div>
