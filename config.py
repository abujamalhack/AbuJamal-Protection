# config.py

import os
from dotenv import load_dotenv

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()

class Config:
    # إعدادات التطبيق العامة
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret-key-default')
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    
    # إعدادات Telegram
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    # إعدادات قاعدة البيانات (يمكن إضافتها لاحقاً)
    # SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# اختيار التكوين بناءً على البيئة
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
