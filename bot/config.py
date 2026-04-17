async def handle_bulk_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج استلام البيانات بصيغة واحدة مع الشعار"""
    user_id = update.effective_user.id
    
    # إذا كان المستخدم يرسل نص طويل (البيانات)
    if update.message.text and len(update.message.text) > 50:
        # تحليل البيانات من النص
        data = parse_bulk_data(update.message.text)
        
        if data:
            # حفظ البيانات
            user_data[user_id] = {'state': STATES['CONFIRM_DATA'], 'data': data}
            
            # انتظار الشعار
            await update.message.reply_text("✅ تم استلام البيانات. 📎 أرسل شعار المنشأة (صورة) الآن.")
            user_data[user_id]['state'] = STATES['LOGO_UPLOAD']
        else:
            await update.message.reply_text("❌ صيغة البيانات غير صحيحة. يرجى استخدام التنسيق المطلوب.")
    
    # إذا كان المستخدم يرسل صورة (الشعار)
    elif update.message.photo:
        await handle_logo_and_generate(update, context)
    
    else:
        await update.message.reply_text("أرسل البيانات أولاً ثم الشعار.")

async def handle_logo_and_generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """استلام الشعار ثم توليد التقرير مباشرة"""
    user_id = update.effective_user.id
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    
    # حفظ الشعار
    logos_dir = f"{OUTPUT_DIR}/logos"
    os.makedirs(logos_dir, exist_ok=True)
    logo_path = f"{logos_dir}/logo_{user_id}.jpg"
    await file.download_to_drive(logo_path)
    
    # إضافة مسار الشعار للبيانات
    user_data[user_id]['data']['custom_logo'] = logo_path
    
    # توليد PDF مباشرة
    await generate_pdf_report(update, context)

def parse_bulk_data(text: str) -> dict:
    """تحويل النص إلى قاموس بيانات"""
    import re
    data = {}
    
    # استخراج البيانات باستخدام تعابير正则
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
        match = re.search(pattern, text)
        if match:
            data[key] = match.group(1).strip()
    
    return data if data else None
