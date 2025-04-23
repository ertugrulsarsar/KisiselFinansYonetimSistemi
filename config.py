import os
from dotenv import load_dotenv
from datetime import timedelta

# .env dosyasını yükle
load_dotenv()

class Config:
    # Uygulama ayarları
    SECRET_KEY = os.getenv('SECRET_KEY', 'gizli-anahtar-degistirin')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Veritabanı bağlantı bilgileri
    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{os.getenv('DB_SERVER', 'DESKTOP-E2G3SHM')}"
        f"/{os.getenv('DB_NAME', 'FinansApp')}"
        f"?driver=ODBC+Driver+17+for+SQL+Server"
        f"&Trusted_Connection=yes"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT ayarları
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-gizli-anahtar-degistirin')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 saat
    
    # Flask-Login ayarları
    SESSION_PROTECTION = 'strong'
    REMEMBER_COOKIE_DURATION = timedelta(days=30)  # 30 gün
    
    # Uygulama sabitleri
    ITEMS_PER_PAGE = 10
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max dosya boyutu
    
    # Template ayarları
    TEMPLATES_AUTO_RELOAD = True
