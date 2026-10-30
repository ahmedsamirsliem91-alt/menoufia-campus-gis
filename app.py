import os
from flask import Flask, render_template, jsonify
import pandas as pd
from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

def get_category_color(category):
    cat = str(category).strip()
    # تخصيص لون تلقائي جذاب حسب الفئة
    color_map = {
        "إدارة": "#2563eb",         # أزرق
        "كليات": "#16a34a",         # أخضر
        "خدمات": "#d97706",        # برتقالي
        "أقسام أكاديمية": "#7c3aed", # بنفسجي
        "معامل متخصصة": "#dc2626", # أحمر
        "ورش ومعامل": "#0891b2",    # تركواز
        "قاعات": "#4f46e5",        # نيلي
        "مكتبات": "#059669",       # أخضر زمردي
        "بوابات": "#57534e"        # رمادي داكن
    }
    return color_map.get(cat, "#2563eb") # اللون الافتراضي أزرق

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/add-location', methods=['POST'])
def add_location():
    excel_path = 'campus_database.xlsx'
    try:
        data = request.json
        xls = pd.ExcelFile(excel_path)
        df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
        
        # إنشاء صف جديد بالمفاتيح المطابقة لأعمدة الإكسل
        new_row = {
            'Building_ID': data.get('building_id'),
            'Building_Name_ar': data.get('building_name_ar'),
            'Building_Name_en': data.get('building_name_en'),
            'Floor_Level_ar': data.get('floor_level_ar'),
            'Floor_Level_en': data.get('floor_level_en'),
            'Section_Or_Office_ar': data.get('section_office_ar'),
            'Section_Or_Office_en': data.get('section_office_en'),
            'Latitude': data.get('latitude'),
            'Longitude': data.get('longitude'),
            'Category': data.get('category'),
            'ISO_17025_Status': data.get('iso_status'),
            'Details_ar': data.get('details_ar'),
            'Details_en': data.get('details_en')
        }
        
        # إلحاق الصف الجديد بـ DataFrame وحفظه في نفس ملف الإكسل
        df_new = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        with pd.ExcelWriter(excel_path, engine='openpyxl', mode='w') as writer:
            df_new.to_excel(writer, sheet_name=xls.sheet_names[0], index=False)
            
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error adding location: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/locations', methods=['GET'])
def get_locations():
    excel_path = 'campus_database.xlsx'
    if not os.path.exists(excel_path):
        return jsonify([])

    try:
        xls = pd.ExcelFile(excel_path)
        df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
        df = df.fillna('')
        df.columns = [str(col).strip() for col in df.columns]
        
        locations = []
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            
            lat = float(row_dict.get('Latitude', row_dict.get('lat', 30.5578)))
            lng = float(row_dict.get('Longitude', row_dict.get('lng', 31.0130)))
            category = str(row_dict.get('Category', 'Academic'))
            
            loc = {
                "lat": lat,
                "lng": lng,
                "building_id": str(row_dict.get('Building_ID', 'N/A')),
                "display_name_ar": str(row_dict.get('Section_Or_Office_ar', row_dict.get('Building_Name_ar', 'موقع'))),
                "display_name_en": str(row_dict.get('Section_Or_Office_en', row_dict.get('Building_Name_en', 'Location'))),
                "building_name_ar": str(row_dict.get('Building_Name_ar', '')),
                "building_name_en": str(row_dict.get('Building_Name_en', '')),
                "floor_level_ar": str(row_dict.get('Floor_Level_ar', '')),
                "floor_level_en": str(row_dict.get('Floor_Level_en', '')),
                "section_office_ar": str(row_dict.get('Section_Or_Office_ar', '')),
                "section_office_en": str(row_dict.get('Section_Or_Office_en', '')),
                "category": category,
                "iso_status": str(row_dict.get('ISO_17025_Status', 'Not Applicable')),
                "details_ar": str(row_dict.get('Details_ar', '')),
                "details_en": str(row_dict.get('Details_en', '')),
                "color": get_category_color(category) # تعيين اللون تلقائياً حسب الفئة
            }
            locations.append(loc)

        return jsonify(locations)
    except Exception as e:
        print(f"Error processing Excel: {e}")
        return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    if port == 5000:
        print("=== Menoufia University Smart GIS Server Running Locally ===")
        print("URL: http://127.0.0.1:5000")
        # تعديل هنا ليكون 0.0.0.0 ليفتح على الآيبي المحلي والشبكة معاً
        app.run(debug=True, host="0.0.0.0", port=5000)
    else:
        print("=== Menoufia University Smart GIS Server Running on Cloud ===")
        app.run(host="0.0.0.0", port=port)
