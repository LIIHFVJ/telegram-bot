import telebot
from telebot import types
import random
import string
import datetime
import os
import hashlib
import hmac
import requests # استخدام requests للتعامل مع Supabase

import base64

# دالة فك التشفير
def d(s): return base64.b64decode(s).decode()

# --- الإعدادات المشفرة ---
API_TOKEN = d('8483983965:AAGlx0T1lbH8g6ZWeVCk8zDf_ySYhgb8G74')
ADMIN_ID = 7126303561
SECRET_KEY = b'martin_super_secret_key_2026'

# --- إعدادات Supabase المشفرة ---
SUPABASE_URL = d('https://snvickveazzkusfnytfn.supabase.co')
SUPABASE_KEY = d('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNudmlja3ZlYXp6a3VzZm55dGZuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgyNTEwMjgsImV4cCI6MjA4MzgyNzAyOH0.LRfr8hwYC-tgOIJq_8TxqhSyD-YL3ITDS5MJyjNWsIw')
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

bot = telebot.TeleBot(API_TOKEN)

# --- وظائف التشفير ---
def encrypt_code(plain_code):
    return hmac.new(SECRET_KEY, plain_code.encode(), hashlib.sha256).hexdigest()[:16].upper()

def generate_random_code(length=12):
    letters_and_digits = string.ascii_uppercase + string.digits
    plain = ''.join(random.choice(letters_and_digits) for i in range(length))
    encrypted = "MAR-" + encrypt_code(plain)
    return plain, encrypted

# --- وظائف Supabase ---
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

# --- لوحة المفاتيح (Menu) ---
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("✨ توليد كود", callback_data="menu_gen")
    btn2 = types.InlineKeyboardButton("  توليد بالجملة", callback_data="menu_bulk")
    btn3 = types.InlineKeyboardButton("  فحص كود", callback_data="ask_info")
    btn4 = types.InlineKeyboardButton("  فك ربط جهاز", callback_data="ask_reset")
    btn5 = types.InlineKeyboardButton("➕ تمديد كود", callback_data="ask_extend")
    btn6 = types.InlineKeyboardButton("  بحث بالـ HWID", callback_data="ask_search_hwid")
    btn7 = types.InlineKeyboardButton("🗑 حذف كود", callback_data="ask_del")
    btn8 = types.InlineKeyboardButton("📊 إحصائيات", callback_data="stats")
    btn9 = types.InlineKeyboardButton("📤 تصدير الأكواد", callback_data="export_codes")
    btn10 = types.InlineKeyboardButton("🧹 تنظيف المنتهي", callback_data="cleanup_expired")
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5, btn6)
    markup.add(btn7, btn8)
    markup.add(btn9, btn10)
    return markup

def gen_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("24 ساعة", callback_data="gen_24h"),
        types.InlineKeyboardButton("7 أيام", callback_data="gen_7d"),
        types.InlineKeyboardButton("14 يوم", callback_data="gen_14d"),
        types.InlineKeyboardButton("شهر", callback_data="gen_1m"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return markup

def bulk_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📦 10 أكواد (24س)", callback_data="bulk_10_24h"),
        types.InlineKeyboardButton("📦 10 أكواد (7أ)", callback_data="bulk_10_7d"),
        types.InlineKeyboardButton("📦 50 كود (شهر)", callback_data="bulk_50_1m"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return markup

# --- وظائف البوت ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ عذراً، هذا البوت خاص بالإدارة فقط.")
        return

    welcome_text = (
        "  **أهلاً بك يا مارتن في لوحة تحكم السكربت**\n\n"
        "استخدم الأزرار أدناه لإدارة الأكواد والتحقق من المشتركين بسهولة."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.from_user.id != ADMIN_ID: return

    if call.data == "menu_gen":
        bot.edit_message_text("✨ اختر مدة الكود الذي تريد توليده:", call.message.chat.id, call.message.message_id, reply_markup=gen_menu())

    elif call.data == "menu_bulk":
        bot.edit_message_text("📦 اختر الكمية والمدة للتوليد بالجملة:", call.message.chat.id, call.message.message_id, reply_markup=bulk_menu())

    elif call.data == "back_main":
        bot.edit_message_text("🏠 القائمة الرئيسية:", call.message.chat.id, call.message.message_id, reply_markup=main_menu())

    elif call.data.startswith("gen_"):
        duration = call.data.replace("gen_", "")
        plain_code, encrypted_code = generate_random_code()
        data = {"code": encrypted_code, "plain_code": plain_code, "duration": duration, "created_at": datetime.datetime.now().isoformat()}
        supabase_insert("codes", data)
        res_text = f"✅ **تم توليد كود جديد ({duration}):**\n\n`{encrypted_code}`"
        bot.edit_message_text(res_text, call.message.chat.id, call.message.message_id, reply_markup=main_menu(), parse_mode="Markdown")

    elif call.data.startswith("bulk_"):
        parts = call.data.split("_")
        count = int(parts[1])
        duration = parts[2]
        
        codes_list = []
        for _ in range(count):
            p, e = generate_random_code()
            supabase_insert("codes", {"code": e, "plain_code": p, "duration": duration, "created_at": datetime.datetime.now().isoformat()})
            codes_list.append(e)
        
        file_path = f"bulk_{duration}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(file_path, "w") as f:
            f.write("\n".join(codes_list))
        
        with open(file_path, "rb") as f:
            bot.send_document(call.message.chat.id, f, caption=f"📦 تم توليد {count} كود بنجاح ({duration})")
        os.remove(file_path)
        bot.answer_callback_query(call.id)

    elif call.data == "ask_info":
        msg = bot.edit_message_text("🔍 أرسل الكود الذي تريد فحصه:", call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(msg, process_info_step)

    elif call.data == "ask_reset":
        msg = bot.edit_message_text("🔄 أرسل الكود لفك ربطه من الجهاز:", call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(msg, process_reset_step)

    elif call.data == "ask_extend":
        msg = bot.edit_message_text("➕ أرسل الكود الذي تريد تمديده (سأضيف له 24 ساعة):", call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(msg, process_extend_step)

    elif call.data == "ask_search_hwid":
        msg = bot.edit_message_text("📱 أرسل الـ HWID للبحث عن الأكواد المربوطة به:", call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(msg, process_search_hwid_step)

    elif call.data == "ask_del":
        msg = bot.edit_message_text("🗑 أرسل الكود لحذفه نهائياً:", call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(msg, process_del_step)

    elif call.data == "stats":
        rows = supabase_select("codes")
        total = len(rows)
        used = len([r for r in rows if r.get('is_used')])
        stats_text = f"📊 **إحصائيات النظام:**\n\n🔹 الإجمالي: `{total}`\n✅ المستخدم: `{used}`\n🆕 المتاح: `{total - used}`"
        bot.edit_message_text(stats_text, call.message.chat.id, call.message.message_id, reply_markup=main_menu(), parse_mode="Markdown")

    elif call.data == "export_codes":
        rows = supabase_select("codes")
        if not rows:
            bot.answer_callback_query(call.id, "❌ لا توجد أكواد في القاعدة.")
            return
        
        file_content = "قائمة الأكواد:\n" + "="*20 + "\n"
        for r in rows:
            status = "مستخدم" if r.get('is_used') else "متاح"
            file_content += f"Code: {r['code']} | Dur: {r['duration']} | Status: {status}\n"
        
        file_path = "all_codes_export.txt"
        with open(file_path, "w", encoding="utf-8") as f: f.write(file_content)
        with open(file_path, "rb") as f: bot.send_document(call.message.chat.id, f, caption="📤 تصدير كافة الأكواد")
        os.remove(file_path)
        bot.answer_callback_query(call.id)

    elif call.data == "cleanup_expired":
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        # ملاحظة: سياسة الحذف تعتمد على مقارنة التاريخ في Supabase
        # للتبسيط هنا سنقوم بحذف الأكواد التي تم استخدامها وانتهى تاريخها فعلياً
        rows = supabase_select("codes", {"is_used": "eq.true"})
        count = 0
        for r in rows:
            if r.get('expiry_date'):
                exp = datetime.datetime.fromisoformat(r['expiry_date'].replace('Z', '+00:00'))
                if datetime.datetime.now(datetime.timezone.utc) > exp:
                    supabase_delete("codes", {"id": f"eq.{r['id']}"})
                    count += 1
        bot.answer_callback_query(call.id, f"🧹 تم تنظيف {count} كود منتهي.")

# --- معالجة المدخلات النصية للأزرار ---

def process_info_step(message):
    target_code = message.text.strip()
    rows = supabase_select("codes", {"code": f"eq.{target_code}"})
    if rows:
        row = rows[0]
        status = "✅ مستخدم" if row.get('is_used') else "🆕 متاح"
        info = f"📊 **تقرير الكود:**\n\n🔑 `{row['code']}`\n🚦 الحالة: {status}\n📱 HWID: `{row.get('hwid') or '---'}`\n📅 انتهاء: `{row.get('expiry_date') or '---'}`"
        bot.send_message(message.chat.id, info, reply_markup=main_menu(), parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ الكود غير موجود.", reply_markup=main_menu())

def process_reset_step(message):
    target_code = message.text.strip()
    supabase_update("codes", {"hwid": None, "is_used": False, "expiry_date": None}, {"code": f"eq.{target_code}"})
    bot.send_message(message.chat.id, f"✅ تم تصفير الكود `{target_code}`.", reply_markup=main_menu())

def process_extend_step(message):
    target_code = message.text.strip()
    rows = supabase_select("codes", {"code": f"eq.{target_code}"})
    if not rows or not rows[0].get('expiry_date'):
        bot.send_message(message.chat.id, "❌ الكود غير مفعل أو غير موجود.", reply_markup=main_menu())
        return
    
    current_expiry = datetime.datetime.fromisoformat(rows[0]['expiry_date'].replace('Z', '+00:00'))
    new_expiry = current_expiry + datetime.timedelta(hours=24)
    supabase_update("codes", {"expiry_date": new_expiry.isoformat()}, {"code": f"eq.{target_code}"})
    bot.send_message(message.chat.id, f"✅ تم تمديد الكود 24 ساعة.\n📅 الموعد الجديد: `{new_expiry.isoformat()}`", reply_markup=main_menu(), parse_mode="Markdown")

def process_search_hwid_step(message):
    hwid = message.text.strip()
    rows = supabase_select("codes", {"hwid": f"eq.{hwid}"})
    if rows:
        text = f"📱 الأكواد المربوطة بـ `{hwid}`:\n\n"
        for r in rows:
            text += f"🔑 `{r['code']}` ({r['duration']})\n"
        bot.send_message(message.chat.id, text, reply_markup=main_menu(), parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ لا توجد أكواد مربوطة بهذا الـ HWID.", reply_markup=main_menu())

def process_del_step(message):
    target_code = message.text.strip()
    status_code = supabase_delete("codes", {"code": f"eq.{target_code}"})
    
    if status_code in [200, 204]:
        bot.send_message(message.chat.id, f"🗑 تم حذف `{target_code}` نهائياً.", reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, "❌ فشل حذف الكود.", reply_markup=main_menu())

# --- API ---
if __name__ == '__main__':
    try:
        me = bot.get_me()
        print(f"\n" + "="*30)
        print(f"🚀 تم تشغيل البوت بنجاح (Supabase Mode)!")
        print(f"🤖 اسم البوت: @{me.username}")
        print(f"📊 قاعدة البيانات: Supabase Cloud")
        print("="*30 + "\n")
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")
    
    bot.polling(none_stop=True)
