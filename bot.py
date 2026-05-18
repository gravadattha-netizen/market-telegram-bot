import telebot
import google.generativeai as genai
import os

# ၁။ Render ရဲ့ Environment Variables ကနေ Key တွေကို ဆွဲယူခြင်း
BOT_TOKEN = os.getenv('BOT_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_KEY')

# ၂။ Bot နှင့် Gemini ကို Setup လုပ်ခြင်း
bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

# ၃။ /start command အတွက် တုံ့ပြန်ချက်
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါ! Market Bot နှိုးနေပါပြီ။ ဘာကူညီပေးရမလဲခင်ဗျာ။")

# ၄။ ပုံမှန်စာသား (AI) အတွက် တုံ့ပြန်ချက်
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "Error တက်နေပါတယ်ခင်ဗျာ။ ခဏနေမှ ပြန်စမ်းကြည့်ပေးပါ။")

# ၅။ Bot ကို စတင်ပတ်ခြင်း (ဒါဟာ အမြဲတမ်း အောက်ဆုံးမှာ ရှိရပါမယ်)
bot.infinity_polling()
