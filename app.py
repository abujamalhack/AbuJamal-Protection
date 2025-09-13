import os
import requests
from datetime import datetime
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename
from config import config

# إنشاء التطبيق
app = Flask(__name__, template_folder='templates')

# تحميل الإعدادات
config_name = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# التحقق من صحة الإعدادات
config[config_name].validate_config()

# إنشاء مجلد التحميلات
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# الصفحة الرئيسية
@app.route('/')
def home():
    return render_template('index.html')

# صفحة التبليغ
@app.route('/report')
def report_page():
    return render_template('report.html')

# استقبال البلاغات
@app.route('/submit_report', methods=['POST'])
def submit_report():
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    report_type = request.form.get('type', '')
    details = request.form.get('details', '')
    image = request.files.get('image')

    if not image or image.filename == '':
        return redirect(url_for('home', error='لم تقم باختيار صورة!'))

    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
    file_extension = image.filename.rsplit('.', 1)[-1].lower() if '.' in image.filename else ''

    if file_extension not in allowed_extensions:
        return redirect(url_for('home', error='نوع الملف غير مدعوم. يُسمح فقط بالصور'))

    image.seek(0, 2)
    file_size = image.tell()
    image.seek(0)

    if file_size > app.config['MAX_CONTENT_LENGTH']:
        return redirect(url_for('home', error='حجم الصورة كبير جداً. الحد الأقصى 5MB'))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = secure_filename(f"{timestamp}_{image.filename}")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        image.save(filepath)
    except Exception as e:
        app.logger.error(f"خطأ في حفظ الملف: {str(e)}")
        return redirect(url_for('home', error='حدث خطأ أثناء حفظ الصورة'))

    telegram_message = f"""
🚨 بلاغ جديد! 🚨
👤 الاسم: {name}
📧 الإيميل: {email}
⚠️ نوع البلاغ: {report_type}
📝 التفاصيل: {details or 'لا توجد تفاصيل إضافية'}
🕒 الوقت: {timestamp}
"""

    try:
        # إرسال الرسالة النصية
        text_url = f"https://api.telegram.org/bot{app.config['TELEGRAM_TOKEN']}/sendMessage"
        text_data = {'chat_id': app.config['TELEGRAM_CHAT_ID'], 'text': telegram_message, 'parse_mode': 'Markdown'}
        requests.post(text_url, json=text_data)

        # إرسال الصورة
        photo_url = f"https://api.telegram.org/bot{app.config['TELEGRAM_TOKEN']}/sendPhoto"
        with open(filepath, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': app.config['TELEGRAM_CHAT_ID']}
            requests.post(photo_url, files=files, data=data)

        return redirect(url_for('home', success='تم استلام البلاغ بنجاح!'))

    except Exception as e:
        app.logger.error(f"خطأ في إرسال البلاغ: {str(e)}")
        return redirect(url_for('home', error='حدث خطأ أثناء إرسال البلاغ. يرجى المحاولة لاحقاً.'))

# خدمة الملفات الثابتة (CSS, JS)
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('templates', filename)

# 404 مخصصة
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# منع الكاش
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
