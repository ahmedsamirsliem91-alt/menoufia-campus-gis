# -*- coding: utf-8 -*-
"""
=============================================================================
محرك الخلفية المستقر لتوجيه المسارات والترجمة الحية (app.py)
المشروع: نظام نظم المعلومات الجغرافية التفاعلي لجامعة المنوفية (Campus GIS)
المؤلف: م. أحمد سمير سليم
=============================================================================
"""

import os
import pandas as pd
from flask import Flask, render_template, jsonify, request
import arabic_reshaper
from bidi.algorithm import get_display

app = Flask(__name__)

EXCEL_FILE_NAME = "campus_database.xlsx"

def format_terminal_text(text):
    """إصلاح وتشكيل النصوص العربية للتيرمنال."""
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text

def load_campus_data():
    """قراءة بيانات الإكسيل المحلي بأمان تام وضمان عدم فقدان أي نقطة جغرافية."""
    if not os.path.exists(EXCEL_FILE_NAME):
        print(format_terminal_text("❌ ملف الإكسيل غير موجود في مسار المشروع!"))
        return []
    try:
        temp_file = "temp_active_db.xlsx"
        with open(EXCEL_FILE_NAME, 'rb') as src, open(temp_file, 'wb') as dst:
            dst.write(src.read())
            
        df = pd.read_excel(temp_file, sheet_name=0)
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
        df = df.fillna('')
        print(format_terminal_text(f"✔ تم تحميل {len(df)} موقعاً جغرافياً بنجاح من قاعدة البيانات."))
        return df.to_dict(orient='records')
    except Exception as e:
        print(format_terminal_text(f"❌ خطأ في قراءة ملف الإكسيل: {e}"))
        return []

def dynamic_translate(arabic_text):
    """محرك ترجمة ديناميكي ذكي يحول المصطلحات الأكاديمية والجغرافية تلقائياً."""
    if not arabic_text:
        return ""
    
    text = str(arabic_text).strip()
    
    replacements = {
        "جامعة المنوفية": "Menoufia University",
        "كلية": "Faculty of",
        "قسم": "Department of",
        "مبنى": "Building",
        "مختبر": "Laboratory",
        "قاعة": "Hall",
        "مكتب": "Office",
        "مسجد": "Mosque",
        "مسرح": "Theatre",
        "بوابة": "Gate",
        "مدينة الطلبة": "Student Dormitories",
        "مركز الخدمة العامة": "Public Service Center",
        "كافتريا": "Cafeteria",
        "أول": "1st", "ثاني": "2nd", "ثالث": "3rd", "أرضي": "Ground Level"
    }
    
    translated = text
    for ar, en in replacements.items():
        translated = translated.replace(ar, en)
        
    return translated

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/locations')
def get_locations():
    """API يوفر كافة المواقع المسجلة للجامعة بدقة عالية."""
    data = load_campus_data()
    processed_data = []
    
    for item in data:
        ar_name = item.get('Building_Name', '')
        ar_sec = item.get('Section_Or_Office', '')
        ar_floor = str(item.get('Floor_Level', ''))
        ar_details = item.get('Details_Arabic', '')
        
        lat_val = item.get('Latitude')
        lng_val = item.get('Longitude')
        
        try:
            lat = float(lat_val) if lat_val else None
            lng = float(lng_val) if lng_val else None
        except (ValueError, TypeError):
            lat, lng = None, None

        if lat and lng:
            processed_data.append({
                'building_id': item.get('Building_ID', 'MNF-CAMPUS'),
                'building_name_ar': ar_name,
                'building_name_en': dynamic_translate(ar_name),
                'floor_level_ar': ar_floor,
                'floor_level_en': dynamic_translate(ar_floor),
                'section_office_ar': ar_sec,
                'section_office_en': dynamic_translate(ar_sec),
                'lat': lat,
                'lng': lng,
                'category': item.get('Category', 'Academic'),
                'iso_status': item.get('ISO_17025_Status', 'N/A'),
                'details_ar': ar_details,
                'details_en': dynamic_translate(ar_details) or "Campus location details available."
            })
            
    return jsonify(processed_data)

if __name__ == '__main__':
    print(format_terminal_text("=== سيرفر خريطة جامعة المنوفية الذكية يعمل الآن باستقرار تام ==="))
    print("http://127.0.0.1:5000")
    app.run(debug=True, port=5000)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port)    
