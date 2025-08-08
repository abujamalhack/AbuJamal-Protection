import os
import requests
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

app = Flask(__name__)

# إعدادات التطبيق
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
UPLOAD_FOLDER = 'uploads'
SECRET_KEY = os.getenv('SECRET_KEY', 'secret-key-12345')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

# إنشاء مجلد التحميلات إذا لم يكن موجوداً
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/report', methods=['POST'])
def report():
    # استقبال البيانات من النموذج
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    report_type = request.form.get('type', '')
    details = request.form.get('details', '')
    image = request.files.get('image')
    
    # التحقق من وجود صورة
    if not image or image.filename == '':
        return redirect(url_for('home', error='لم تقم باختيار صورة!'))
    
    # حفظ الصورة
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = secure_filename(f"{timestamp}_{image.filename}")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(filepath)
    
    # إعداد رسالة التليجرام
    telegram_message = f"""
🚨 **بلاغ جديد!** 🚨
👤 **الاسم:** {name}
📧 **الإيميل:** {email}
⚠️ **نوع البلاغ:** {report_type}
📝 **التفاصيل:** {details or 'لا توجد تفاصيل إضافية'}
🕒 **الوقت:** {timestamp}
"""
    
    try:
        # إرسال الرسالة النصية
        text_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        text_data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': telegram_message,
            'parse_mode': 'Markdown'
        }
        requests.post(text_url, json=text_data)
        
        # إرسال الصورة
        photo_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        with open(filepath, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': TELEGRAM_CHAT_ID}
            requests.post(photo_url, files=files, data=data)
        
        return redirect(url_for('home', success='تم استلام البلاغ بنجاح! شكراً لمساهمتك.'))
    
    except Exception as e:
        app.logger.error(f"خطأ في إرسال البلاغ: {str(e)}")
        return redirect(url_for('home', error='حدث خطأ أثناء إرسال البلاغ. يرجى المحاولة لاحقاً.'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
