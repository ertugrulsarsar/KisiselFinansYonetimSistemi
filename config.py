import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class Config:
    # Veritabanı bağlantı bilgileri
    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://@DESKTOP-E2G3SHM/FinansApp"
        f"?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT ayarları
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'gizli-anahtar-degistirin')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 saat
    
    # Uygulama ayarları
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'gizli-anahtar-degistirin')
