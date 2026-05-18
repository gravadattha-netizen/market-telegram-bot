import telebot
import google.generativeai as genai
import os

# Render ရဲ့ Environment Variables ကနေ Key တွေကို ဆွဲယူခြင်း
BOT_TOKEN = os.getenv('BOT_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါ! Market Bot နိုးနေပါပြီ။")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "Error တက်နေပါတယ်ခင်ဗျာ။")

bot.infinity_polling()
