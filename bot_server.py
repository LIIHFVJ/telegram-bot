import telebot
from telebot import types
import random
import string
import datetime
import os
import hashlib
import hmac
import requests
import base64

def ds(s):
    return base64.b64decode(s).decode()

TITLE = "---"
API_TOKEN = "dNzg2NDgyMTYxMjpBQUhuOTlfWVZuX29ZeU9uZEQ4QnYtMUJxV3AzMllJM2VQOA"
ADMIN_ID = 5626244431
SECRET_KEY = "bmartinsupersecretkey2026"
SUPABASE_URL = "daHR0cHM6Ly9zbnZpY2t2ZWF6emt1c2ZueXRmbi5zdXBhYmFzZS5jbw"
SUPABASE_KEY = "dZXlKaGJHY2lPaUpIUXpJM05pSXNJbkI1Y0NJNklrcFhWQ0o5LmV5SnBjM01pT2lKemRYQmFZV0poYzJVMklsSmxaaUk2SW5KdWRtbGphM1p2WVdSM2EzVnpaVzV1ZVhSZmJpSXNJbkp2YkdVaU9pSmhibTluSWx0cE1YUWlPakUzTmpneU5URXdNamdmSW1WNGNDSTZNalE0TXpneU56QXlPSDAuTFJmcjhod1lDLXRnT0lKcV84VHhxaFN5RC1ZTDNJVERTTU1MeWpOV3NIdw"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

bot = telebot.TeleBot(API_TOKEN)

def encrypt_code(plain_code):
    return hmac.new(SECRET_KEY.encode(), plain_code.encode(), hashlib.sha256).hexdigest()[:16].upper()

def generate_random_code(length=12):
    letters_and_digits = string.ascii_uppercase + string.digits
    plain = ''.join(random.choice(letters_and_digits) for i in range(length))
    encrypted = "MAR-" + encrypt_code(plain)
    return plain, encrypted

def supabase_insert(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    response = requests.post(url, headers=HEADERS, json=data)
    return response.json()

def supabase_select(table, filters=None):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = filters if filters else {}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()

def supabase_update(table, data, filters):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    response = requests.patch(url, headers=HEADERS, json=data, params=filters)
    return response.json()

def supabase_delete(table, filters):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    response = requests.delete(url, headers=HEADERS, params=filters)
    return response.status_code

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("جنرات كود", callback_data="menu_gen")
    btn2 = types.InlineKeyboardButton("جنرات بالجملة", callback_data="menu_bulk")
    btn3 = types.InlineKeyboardButton("المعلومات", callback_data="ask_info")
    btn4 = types.InlineKeyboardButton("اعادة تعيين", callback_data="ask_reset")
    btn5 = types.InlineKeyboardButton("تمديد", callback_data="ask_extend")
    btn6 = types.InlineKeyboardButton("البحث HWID", callback_data="ask_search_hwid")
    btn7 = types.InlineKeyboardButton("حذف", callback_data="ask_del")
    btn8 = types.InlineKeyboardButton("الاحصائيات", callback_data="stats")
    btn9 = types.InlineKeyboardButton("تصدير الاكواد", callback_data="export_codes")
    btn10 = types.InlineKeyboardButton("تنظيف منتهية الصلاحية", callback_data="cleanup_expired")
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5, btn6)
    markup.add(btn7, btn8)
    markup.add(btn9, btn10)
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "غير مصرح")
        return
    welcome_text = "مرحبا بك في بوت ادارة الاكواد"
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.from_user.id != ADMIN_ID:
        return
    
    if call.data == "menu_gen":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("24 ساعة", callback_data="gen_24h"),
            types.InlineKeyboardButton("7 ايام", callback_data="gen_7d"),
            types.InlineKeyboardButton("14 يوم", callback_data="gen_14d"),
            types.InlineKeyboardButton("شهر", callback_data="gen_1m"),
            types.InlineKeyboardButton("رجوع", callback_data="back_main")
        )
        bot.edit_message_text("اختر المدة:", call.message.chat.id, call.message.message_id, reply_markup=markup)
    
    elif call.data.startswith("gen_"):
        duration = call.data.replace("gen_", "")
        plain_code, encrypted_code = generate_random_code()
        data = {"code": encrypted_code, "plaincode": plain_code, "duration": duration, "createdat": datetime.datetime.now().isoformat()}
        supabase_insert("codes", data)
        res_text = f"✅ تم انشاء الكود\n\nالكود: `{encrypted_code}`\nالمدة: {duration}"
        bot.edit_message_text(res_text, call.message.chat.id, call.message.message_id, reply_markup=main_menu(), parse_mode="Markdown")
    
    elif call.data == "back_main":
        bot.edit_message_text("القائمة الرئيسية:", call.message.chat.id, call.message.message_id, reply_markup=main_menu())
    
    elif call.data == "ask_info":
        msg = bot.edit_message_text("ادخل الكود:", call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(msg, process_info_step)
    
    elif call.data == "stats":
        rows = supabase_select("codes")
        total = len(rows)
        used = len([r for r in rows if r.get("isused")])
        stats_text = f"📊 الاحصائيات:\n\nالاجمالي: {total}\nالمستخدم: {used}\nالمتبقي: {total - used}"
        bot.edit_message_text(stats_text, call.message.chat.id, call.message.message_id, reply_markup=main_menu(), parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def process_info_step(message):
    target_code = message.text.strip()
    rows = supabase_select("codes", {"code": f"eq.{target_code}"})
    if rows:
        row = rows[0]
        status = "مستخدم" if row.get("isused") else "متاح"
        info = f"\n✅ الكود: {row['code']}\nالحالة: {status}\nHWID: {row.get('hwid') or '---'}\nتاريخ الانتهاء: {row.get('expirydate') or '---'}"
        bot.send_message(message.chat.id, info, reply_markup=main_menu(), parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ الكود غير موجود.", reply_markup=main_menu())

if __name__ == "__main__":
    try:
        me = bot.get_me()
        print(f"{'='*30}")
        print(f"البوت {me.username} يعمل الآن")
        print(f"{'='*30}")
    except Exception as e:
        print(f"خطأ: {e}")
    bot.polling(none_stop=True)
