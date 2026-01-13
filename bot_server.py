import telebot
from telebot import types
import random
import string
import datetime
import os

API_TOKEN = "8483983965:AAEBJkc8tqQi6Gn0-pFcrD-uVYwVh2iQfuc"
ADMIN_ID = 7126303561

bot = telebot.TeleBot(API_TOKEN)

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('جنرات كود', callback_data='menu_gen')
    btn2 = types.InlineKeyboardButton('إحصائيات', callback_data='stats')
    markup.add(btn1, btn2)
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "غير مصرح")
        return
    welcome_text = "مرحبا بك في بوت التليجرام"
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.from_user.id != ADMIN_ID:
        return
    
    if call.data == "menu_gen":
        bot.edit_message_text("جنرات كود جديد", call.message.chat.id, call.message.message_id, reply_markup=main_menu())
    elif call.data == "stats":
        bot.edit_message_text("الإحصائيات", call.message.chat.id, call.message.message_id, reply_markup=main_menu())

if __name__ == "__main__":
    try:
        me = bot.get_me()
        print(f"Bot {me.username} is running!")
    except Exception as e:
        print(f"Error: {e}")
    bot.polling(none_stop=True)
