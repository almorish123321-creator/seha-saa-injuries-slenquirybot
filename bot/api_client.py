#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Client for Seha Website Integration
عميل API لربط البوت بموقع صحة
"""

import requests
import json
import logging
from datetime import datetime
from config import API_FULL_URL

# إعداد التسجيل
logger = logging.getLogger(__name__)

def calculate_duration_days(admission_date, discharge_date):
    """حساب عدد الأيام بين تاريخين"""
    try:
        admission_parts = admission_date.split('-')
        discharge_parts = discharge_date.split('-')
        
        if len(admission_parts) == 3 and len(discharge_parts) == 3:
            admission_dt = datetime(int(admission_parts[2]), int(admission_parts[1]), int(admission_parts[0]))
            discharge_dt = datetime(int(discharge_parts[2]), int(discharge_parts[1]), int(discharge_parts[0]))
            days = (discharge_dt - admission_dt).days + 1
            return max(1, days)
        return 1
    except Exception as e:
        logger.error(f"خطأ في حساب الأيام: {e}")
        return 1

def generate_service_code(id_number, admission_date, discharge_date):
    """توليد رمز خدمة فريد"""
    try:
        import random
        now = datetime.now()
        # PSL + رقم عشوائي + تاريخ
        random_part = str(random.randint(10000000, 99999999))
        return f"PSL{random_part}{now.strftime('%d%m%Y')}"
    except Exception as e:
        logger.error(f"خطأ في توليد رمز الخدمة: {e}")
        return f"PSL{datetime.now().strftime('%Y%m%d%H%M%S')}"

def convert_date_format(date_str):
    """تحويل التاريخ من صيغة dd-mm-yyyy إلى yyyy-mm-dd"""
    try:
        parts = date_str.split('-')
        if len(parts) == 3:
            return f"{parts[2]}-{parts[1]}-{parts[0]}"
        return date_str
    except:
        return date_str

def send_leave_data_to_api(user_data):
    """إرسال بيانات الإجازة إلى API الموقع (بصيغة مطابقة لموقع Flask)"""
    try:
        # توليد رمز الخدمة
        service_code = generate_service_code(
            user_data.get('id_number', ''),
            user_data.get('admission_date_gregorian', ''),
            user_data.get('discharge_date_gregorian', '')
        )
        
        # حساب مدة الإجازة
        duration_days = calculate_duration_days(
            user_data.get('admission_date_gregorian', ''),
            user_data.get('discharge_date_gregorian', '')
        )
        
        # تحويل التواريخ إلى الصيغة المطلوبة (yyyy-mm-dd)
        admission_date = convert_date_format(user_data.get('admission_date_gregorian', ''))
        discharge_date = convert_date_format(user_data.get('discharge_date_gregorian', ''))
        report_issue_date = convert_date_format(user_data.get('issue_date_gregorian', ''))
        
        # إعداد البيانات بصيغة مطابقة لموقع Flask
        api_data = {
            'service_code': service_code,
            'identity_number': user_data.get('id_number', ''),
            'patient_name_ar': user_data.get('patient_name_ar', ''),
            'patient_name_en': user_data.get('patient_name_en', ''),
            'nationality_ar': user_data.get('nationality_ar', ''),
            'nationality_en': user_data.get('nationality_en', ''),
            'workplace_ar': user_data.get('employer_ar', ''),
            'workplace_en': user_data.get('employer_en', ''),
            'doctor_name_ar': user_data.get('doctor_name_ar', ''),
            'doctor_name_en': user_data.get('doctor_name_en', ''),
            'job_title_ar': user_data.get('position_ar', ''),
            'job_title_en': user_data.get('position_en', ''),
            'admission_date_gregorian': admission_date,
            'admission_date_hijri': user_data.get('admission_date_hijri', ''),
            'discharge_date_gregorian': discharge_date,
            'discharge_date_hijri': user_data.get('discharge_date_hijri', ''),
            'report_issue_date': report_issue_date,
            'facility_name_ar': user_data.get('hospital_name_ar', ''),
            'facility_name_en': user_data.get('hospital_name_en', ''),
            'report_time': user_data.get('time', ''),
            'duration_days': duration_days
        }
        
        # إرسال البيانات
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json'
        }
        
        logger.info(f"إرسال البيانات إلى API: {API_FULL_URL}")
        logger.info(f"البيانات المرسلة: {json.dumps(api_data, ensure_ascii=False)}")
        
        response = requests.post(
            API_FULL_URL,
            json=api_data,
            headers=headers,
            timeout=30
        )
        
        # التحقق من الاستجابة
        if response.status_code == 200:
            try:
                result = response.json()
                logger.info(f"استجابة الخادم: {json.dumps(result, ensure_ascii=False)}")
                
                # محاولة الحصول على رمز الخدمة من الاستجابة
                leave_id = result.get('service_code') or result.get('id') or service_code
                
                return {
                    'success': True,
                    'message': 'تم حفظ بيانات الإجازة في النظام بنجاح',
                    'leave_id': leave_id,
                    'data': result
                }
            except:
                return {
                    'success': True,
                    'message': 'تم حفظ بيانات الإجازة في النظام بنجاح',
                    'leave_id': service_code,
                    'data': {}
                }
        else:
            logger.error(f"خطأ HTTP {response.status_code}: {response.text}")
            return {
                'success': False,
                'message': f"خطأ في الاتصال بالخادم (HTTP {response.status_code})",
                'leave_id': service_code
            }
            
    except requests.exceptions.ConnectionError:
        logger.error("فشل في الاتصال بالخادم")
        return {
            'success': False,
            'message': 'فشل في الاتصال بالخادم. تأكد من تشغيل الموقع.',
            'leave_id': service_code if 'service_code' in locals() else 'غير محدد'
        }
    except requests.exceptions.Timeout:
        logger.error("انتهت مهلة الاتصال")
        return {
            'success': False,
            'message': 'انتهت مهلة الاتصال بالخادم',
            'leave_id': service_code if 'service_code' in locals() else 'غير محدد'
        }
    except Exception as e:
        logger.error(f"خطأ غير متوقع في إرسال البيانات: {e}")
        return {
            'success': False,
            'message': f'خطأ غير متوقع: {str(e)}',
            'leave_id': service_code if 'service_code' in locals() else 'غير محدد'
        }

if __name__ == "__main__":
    # اختبار سريع
    test_data = {
        'id_number': '1234567890',
        'patient_name_ar': 'أحمد محمد السعيد',
        'patient_name_en': 'Ahmed Mohammed Al-Saeed',
        'nationality_ar': 'سعودي',
        'nationality_en': 'Saudi',
        'employer_ar': 'شركة النخبة',
        'employer_en': 'Elite Company',
        'doctor_name_ar': 'د. نبيل حنا نصر',
        'doctor_name_en': 'Dr. Nabil Hanna Nasr',
        'position_ar': 'طبيب عام',
        'position_en': 'General Practitioner',
        'issue_date_gregorian': '20-01-2025',
        'admission_date_gregorian': '18-01-2025',
        'admission_date_hijri': '18-04-1446',
        'discharge_date_gregorian': '20-01-2025',
        'discharge_date_hijri': '20-04-1446',
        'hospital_name_ar': 'مستشفى الملك فهد',
        'hospital_name_en': 'King Fahd Hospital',
        'time': '10:30 AM'
    }
    
    result = send_leave_data_to_api(test_data)
    print(f"نتيجة الاختبار: {json.dumps(result, ensure_ascii=False, indent=2)}")
