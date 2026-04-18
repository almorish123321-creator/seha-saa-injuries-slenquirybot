#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seha Sick Leave Bot
بوت تيليجرام لتوليد تقارير الإجازة المرضية
"""

import logging
import os
import re
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, ADMIN_USER_ID, OUTPUT_DIR
from pdf_generator_v4 import generate_sick_leave_pdf
from api_client import send_leave_data_to_api

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# حالات المحادثة
STATES = {
    'START': 0,
    'PATIENT_NAME_AR': 1,
    'PATIENT_NAME_EN': 2,
    'ID_NUMBER': 3,
    'NATIONALITY_AR': 4,
    'NATIONALITY_EN': 5,
    'EMPLOYER_AR': 6,
    'EMPLOYER_EN': 7,
    'DOCTOR_NAME_AR': 8,
    'DOCTOR_NAME_EN': 9,
    'POSITION_AR': 10,
    'POSITION_EN': 11,
    'ADMISSION_DATE_GREGORIAN': 12,
    'ADMISSION_DATE_HIJRI': 13,
    'DISCHARGE_DATE_GREGORIAN': 14,
    'DISCHARGE_DATE_HIJRI': 15,
    'ISSUE_DATE_GREGORIAN': 16,
    'HOSPITAL_NAME_AR': 17,
    'HOSPITAL_NAME_EN': 18,
    'TIME': 19,
    'LOGO_UPLOAD': 20,
    'CONFIRM_DATA': 21,
    'GENERATE_REPORT': 22
}

# تخزين بيانات المستخدمين
user_data = {}

def parse_bulk_data(text: str) -> dict:
    """تحويل النص إلى قاموس بيانات (للإدخال السريع)"""
    data = {}
    
    patterns = {
        'patient_name_ar': r'اسم المريض \(عربي\):\s*(.+)',
        'patient_name_en': r'اسم المريض \(إنجليزي\):\s*(.+)',
        'id_number': r'رقم الهوية:\s*(.+)',
        'nationality_ar': r'الجنسية \(عربي\):\s*(.+)',
        'nationality_en': r'الجنسية \(إنجليزي\):\s*(.+)',
        'employer_ar': r'جهة العمل \(عربي\):\s*(.+)',
        'employer_en': r'جهة العمل \(إنجليزي\):\s*(.+)',
        'doctor_name_ar': r'اسم الطبيب \(عربي\):\s*(.+)',
        'doctor_name_en': r'اسم الطبيب \(إنجليزي\):\s*(.+)',
        'position_ar': r'المسمى الوظيفي \(عربي\):\s*(.+)',
        'position_en': r'المسمى الوظيفي \(إنجليزي\):\s*(.+)',
        'admission_date_gregorian': r'تاريخ الدخول \(ميلادي\):\s*(.+)',
        'admission_date_hijri': r'تاريخ الدخول \(هجري\):\s*(.+)',
        'discharge_date_gregorian': r'تاريخ الخروج \(ميلادي\):\s*(.+)',
        'discharge_date_hijri': r'تاريخ الخروج \(هجري\):\s*(.+)',
        'issue_date_gregorian': r'تاريخ إصدار التقرير:\s*(.+)',
        'hospital_name_ar': r'اسم المنشأة \(عربي\):\s*(.+)',
        'hospital_name_en': r'اسم المنشأة \(إنجليزي\):\s*(.+)',
        'time': r'الوقت:\s*(.+)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data[key] = match.group(1).strip()
    
    return data if data else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /start"""
    user_id = update.effective_user.id
    
    welcome_message = """👋 مرحبًا بك في بوت منصة صحة الرسمي

يقدم هذا البوت خدمة إصدار تقرير إجازة مرضية رسمي بصيغة PDF معتمد من وزارة الصحة السعودية.

🔒 الاستخدام مخصص فقط للمستخدمين المعتمدين.

⚙️ طريقتان للاستخدام:
1️⃣ اضغط على زر "🆕 إنشاء تقرير جديد" للإدخال خطوة بخطوة
2️⃣ أو أرسل جميع البيانات دفعة واحدة (انظر التنسيق المطلوب)

لبدء إنشاء تقرير، اضغط الزر أدناه:"""
    
    keyboard = [[KeyboardButton("🆕 إنشاء تقرير جديد")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    user_data[user_id] = {'state': STATES['START']}

async def handle_bulk_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج استلام البيانات بصيغة واحدة (دفعة واحدة)"""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # محاولة تحليل البيانات
    data = parse_bulk_data(message_text)
    
    if data and len(data) >= 5:  # على الأقل 5 حقول أساسية
        user_data[user_id] = {'state': STATES['LOGO_UPLOAD'], 'data': data}
        
        summary = f"""📝 تم استلام البيانات بنجاح!

👤 اسم المريض: {data.get('patient_name_ar', 'غير محدد')}
🆔 رقم الهوية: {data.get('id_number', 'غير محدد')}
🏥 المنشأة: {data.get('hospital_name_ar', 'غير محدد')}
👨‍⚕️ الطبيب: {data.get('doctor_name_ar', 'غير محدد')}

📎 أرسل شعار المنشأة (صورة) الآن لإكمال التقرير."""
        
        await update.message.reply_text(summary)
    else:
        await update.message.reply_text("❌ لم أتمكن من تحليل البيانات. تأكد من التنسيق الصحيح أو استخدم الزر لإنشاء تقرير جديد.")

async def handle_new_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج زر إنشاء تقرير جديد"""
    user_id = update.effective_user.id
    
    if update.message.text == "🆕 إنشاء تقرير جديد":
        user_data[user_id] = {'state': STATES['PATIENT_NAME_AR'], 'data': {}}
        
        message = "📌 يرجى إدخال البيانات بشكل صحيح.\n\n✍️ يرجى إدخال اسم المريض باللغة العربية"
        
        keyboard = [[KeyboardButton("الخطوة التالية")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        
        await update.message.reply_text(message, reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج الرسائل النصية (للإدخال خطوة بخطوة)"""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    if user_id not in user_data:
        await start(update, context)
        return
    
    current_state = user_data[user_id]['state']
    
    if current_state == STATES['START']:
        if message_text == "🆕 إنشاء تقرير جديد":
            await handle_new_report(update, context)
    
    elif current_state == STATES['PATIENT_NAME_AR']:
        if message_text != "الخطوة التالية":
            user_data[user_id]['data']['patient_name_ar'] = message_text
        await ask_patient_name_en(update, context)
    
    elif current_state == STATES['PATIENT_NAME_EN']:
        if message_text != "الخطوة التالية":
            user_data[user_id]['data']['patient_name_en'] = message_text
        await ask_id_number(update, context)
    
    elif current_state == STATES['ID_NUMBER']:
        if message_text != "الخطوة التالية":
            user_data[user_id]['data']['id_number'] = message_text
        await ask_nationality_ar(update, context)
    
    elif current_state == STATES['NATIONALITY_AR']:
        if message_text != "الخطوة التالية":
            user_data[user_id]['data']['nationality_ar'] = message_text
        await ask_nationality_en(update, context)
    
    elif current_state == STATES['NATIONALITY_EN']:
        if message_text != "الخطوة التالية":
            user_data[user_id]['data']['nationality_en'] = message_text
        await ask_employer_ar(update, context)
    
    elif current_state == STATES['EMPLOYER_AR']:
        if message_text != "الخطوة التالية":
            user_data[user_id]['data']['employer_ar'] = message_text
        await ask_employer_en(update, context)
    
    elif current_state == STATES['EMPLOYER_EN']:
        if message_text != "الخطوة التالية":
            user_data[user_id]['data']['employer_en'] = message_text
        await ask_doctor_name_ar(update, context)
    
    elif current_state == STATES['DOCTOR_NAME_AR']:
        if message_text != "الخطوة التالية":
            user_data[user_id]['data']['doctor_name_ar'] = message_text
        await ask_doctor_name_en(update, context)
    
    elif current_state == STATES['DOCTOR_NAME_EN']:
        if message_text != "الخطوة التالية":
            user_data[user_id]['data']['doctor_name_en'] = message_text
        await ask_position_ar(update, context)
    
    elif current_state == STATES['POSITION_AR']:
        if message_text != "الخطوة التالية":
            user_data[user_id]['data']['position_ar'] = message_text
        await ask_position_en(update, context)
    
    elif current_state == STATES['POSITION_EN']:
        if message_text != "الخطوة التالية":
            user_data[user_id]['data']['position_en'] = message_text
        await ask_admission_date_gregorian(update, context)
    
    elif current_state == STATES['ADMISSION_DATE_GREGORIAN']:
        if message_text != "الخطوة التالية":
            user_data[user_id]['data']['admission_date_gregorian'] = message_text
        await ask_admission_date_hijri(update, context)
    
    elif current_state == STATES['ADMISSION_DATE_HIJRI']:
        if message_text != "الخطوة التالية":
            user_data[user_id]['data']['admission_date_hijri'] = message_text
        await ask_discharge_date_gregorian(update, context)
    
    elif current_state == STATES['DISCHARGE_DATE_GREGORIAN']:
        if message_text != "الخطوة التالية":
            user_data[user_id]['data']['discharge_date_gregorian'] = message_text
        await ask_discharge_date_hijri(update, context)
    
    elif current_state == STATES['DISCHARGE_DATE_HIJRI']:
        if message_text != "الخطوة التالية":
            user_data[user_id]['data']['discharge_date_hijri'] = message_text
        await ask_issue_date_gregorian(update, context)
    
    elif current_state == STATES['ISSUE_DATE_GREGORIAN']:
        if message_text != "الخطوة التالية":
            user_data[user_id]['data']['issue_date_gregorian'] = message_text
        await ask_hospital_name_ar(update, context)
    
    elif current_state == STATES['HOSPITAL_NAME_AR']:
        if message_text != "الخطوة التالية":
            user_data[user_id]['data']['hospital_name_ar'] = message_text
        await ask_hospital_name_en(update, context)
    
    elif current_state == STATES['HOSPITAL_NAME_EN']:
        if message_text != "الخطوة التالية":
            user_data[user_id]['data']['hospital_name_en'] = message_text
        await ask_time(update, context)
    
    elif current_state == STATES['TIME']:
        if message_text != "الخطوة التالية":
            user_data[user_id]['data']['time'] = message_text
        await ask_logo_upload(update, context)
    
    elif current_state == STATES['LOGO_UPLOAD']:
        if message_text == "✅ تأكد من البيانات":
            await confirm_data(update, context)
    
    elif current_state == STATES['CONFIRM_DATA']:
        if message_text == "📄 حفظ وإرسال التقرير بصيغة PDF":
            await generate_pdf_report(update, context)
        elif message_text == "🖼️ حفظ وإرسال التقرير بصيغة PNG":
            await generate_png_report(update, context)

async def ask_patient_name_en(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id]['state'] = STATES['PATIENT_NAME_EN']
    message = "✍️ يرجى إدخال اسم المريض باللغة الإنجليزية"
    keyboard = [[KeyboardButton("الخطوة التالية")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def ask_id_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id]['state'] = STATES['ID_NUMBER']
    message = "✍️ يرجى إدخال رقم الهوية"
    keyboard = [[KeyboardButton("الخطوة التالية")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def ask_nationality_ar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id]['state'] = STATES['NATIONALITY_AR']
    message = "✍️ يرجى إدخال الجنسية باللغة العربية"
    keyboard = [[KeyboardButton("الخطوة التالية")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def ask_nationality_en(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id]['state'] = STATES['NATIONALITY_EN']
    message = "✍️ يرجى إدخال الجنسية باللغة الإنجليزية"
    keyboard = [[KeyboardButton("الخطوة التالية")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def ask_employer_ar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id]['state'] = STATES['EMPLOYER_AR']
    message = "✍️ يرجى إدخال جهة العمل باللغة العربية"
    keyboard = [[KeyboardButton("الخطوة التالية")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def ask_employer_en(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id]['state'] = STATES['EMPLOYER_EN']
    message = "✍️ يرجى إدخال جهة العمل باللغة الإنجليزية"
    keyboard = [[KeyboardButton("الخطوة التالية")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def ask_doctor_name_ar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id]['state'] = STATES['DOCTOR_NAME_AR']
    message = "✍️ يرجى إدخال اسم الطبيب المعالج باللغة العربية"
    keyboard = [[KeyboardButton("الخطوة التالية")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def ask_doctor_name_en(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id]['state'] = STATES['DOCTOR_NAME_EN']
    message = "✍️ يرجى إدخال اسم الطبيب المعالج باللغة الإنجليزية"
    keyboard = [[KeyboardButton("الخطوة التالية")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def ask_position_ar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id]['state'] = STATES['POSITION_AR']
    message = "✍️ يرجى إدخال المسمى الوظيفي باللغة العربية"
    keyboard = [[KeyboardButton("الخطوة التالية")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def ask_position_en(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id]['state'] = STATES['POSITION_EN']
    message = "✍️ يرجى إدخال المسمى الوظيفي باللغة الإنجليزية"
    keyboard = [[KeyboardButton("الخطوة التالية")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def ask_admission_date_gregorian(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id]['state'] = STATES['ADMISSION_DATE_GREGORIAN']
    message = "📅 يرجى إدخال تاريخ الدخول (ميلادي)"
    keyboard = [[KeyboardButton("الخطوة التالية")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def ask_admission_date_hijri(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id]['state'] = STATES['ADMISSION_DATE_HIJRI']
    message = "📅 يرجى إدخال تاريخ الدخول (هجري)"
    keyboard = [[KeyboardButton("الخطوة التالية")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def ask_discharge_date_gregorian(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id]['state'] = STATES['DISCHARGE_DATE_GREGORIAN']
    message = "📅 يرجى إدخال تاريخ الخروج (ميلادي)"
    keyboard = [[KeyboardButton("الخطوة التالية")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def ask_discharge_date_hijri(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id]['state'] = STATES['DISCHARGE_DATE_HIJRI']
    message = "📅 يرجى إدخال تاريخ الخروج (هجري)"
    keyboard = [[KeyboardButton("الخطوة التالية")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def ask_issue_date_gregorian(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id]['state'] = STATES['ISSUE_DATE_GREGORIAN']
    message = "📅 يرجى إدخال تاريخ إصدار التقرير (ميلادي)"
    keyboard = [[KeyboardButton("الخطوة التالية")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def ask_hospital_name_ar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id]['state'] = STATES['HOSPITAL_NAME_AR']
    message = "🏥 يرجى إدخال اسم المستشفى/المجمع/المستوصف بالعربية"
    keyboard = [[KeyboardButton("الخطوة التالية")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def ask_hospital_name_en(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id]['state'] = STATES['HOSPITAL_NAME_EN']
    message = "🏥 يرجى إدخال اسم المستشفى/المجمع/المستوصف بالإنجليزية"
    keyboard = [[KeyboardButton("الخطوة التالية")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def ask_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id]['state'] = STATES['TIME']
    message = "⏰ يرجى إدخال الوقت (مثل: 11:30 AM)"
    keyboard = [[KeyboardButton("الخطوة التالية")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def ask_logo_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id]['state'] = STATES['LOGO_UPLOAD']
    message = "📎 يرجى إرسال شعار المنشأة كصورة"
    keyboard = [[KeyboardButton("✅ تأكد من البيانات")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def confirm_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id]['state'] = STATES['CONFIRM_DATA']
    
    data = user_data[user_id]['data']
    
    summary = f"""📝 ملخص البيانات المدخلة:

👤 اسم المريض (عربي): {data.get('patient_name_ar', 'غير محدد')}
🆔 رقم الهوية: {data.get('id_number', 'غير محدد')}
🏥 المنشأة: {data.get('hospital_name_ar', 'غير محدد')}
👨‍⚕️ الطبيب: {data.get('doctor_name_ar', 'غير محدد')}
📅 تاريخ الدخول: {data.get('admission_date_gregorian', 'غير محدد')}
📅 تاريخ الخروج: {data.get('discharge_date_gregorian', 'غير محدد')}"""
    
    keyboard = [[KeyboardButton("📄 حفظ وإرسال التقرير بصيغة PDF")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(summary, reply_markup=reply_markup)

async def generate_pdf_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """توليد تقرير PDF وإرسال البيانات إلى الموقع"""
    user_id = update.effective_user.id
    
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        data = user_data[user_id]['data']
        pdf_path = generate_sick_leave_pdf(data, user_id)
        
        with open(pdf_path, 'rb') as pdf_file:
            await update.message.reply_document(
                document=pdf_file,
                filename=os.path.basename(pdf_path),
                caption="✅ تم إنشاء تقرير الإجازة المرضية بنجاح!"
            )
        
        await update.message.reply_text("🔄 جاري حفظ البيانات في النظام...")
        
        api_result = send_leave_data_to_api(data)
        
        if api_result['success']:
            success_message = f"""✅ تم حفظ بيانات الإجازة في النظام بنجاح!

🆔 رمز الإجازة: {api_result['leave_id']}

يمكنك الاستعلام عن الإجازة من الموقع باستخدام رقم الهوية: {data.get('id_number', '')}"""
            await update.message.reply_text(success_message)
        else:
            error_message = f"""⚠️ تم إنشاء التقرير ولكن حدث خطأ في حفظ البيانات:

❌ {api_result['message']}

🆔 رمز الإجازة: {api_result['leave_id']}"""
            await update.message.reply_text(error_message)
        
        user_data[user_id] = {'state': STATES['START']}
        
        keyboard = [[KeyboardButton("🆕 إنشاء تقرير جديد")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("يمكنك إنشاء تقرير جديد:", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"خطأ في توليد PDF: {e}")
        await update.message.reply_text("❌ حدث خطأ في توليد التقرير. يرجى المحاولة مرة أخرى.")

async def generate_png_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🚧 ميزة PNG قيد التطوير...")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id in user_data and user_data[user_id]['state'] == STATES['LOGO_UPLOAD']:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        
        logos_dir = f"{OUTPUT_DIR}/logos"
        os.makedirs(logos_dir, exist_ok=True)
        
        logo_path = f"{logos_dir}/logo_{user_id}.jpg"
        await file.download_to_drive(logo_path)
        
        user_data[user_id]['data']['custom_logo'] = logo_path
        await update.message.reply_text("✅ تم حفظ الشعار بنجاح! اضغط '✅ تأكد من البيانات' للمتابعة.")

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    
    # معالج الرسائل النصية (يدعم الدفعة الواحدة)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex('^🆕'), handle_bulk_message))
    application.add_handler(MessageHandler(filters.Regex('^🆕'), handle_new_report))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("🤖 بدء تشغيل بوت صحة للإجازات المرضية...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
