from flask import Flask, redirect, url_for
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.models import init_db
from app.routes import api_bp, auth_bp, transaction_bp, category_bp
from config import Config

def create_app():
    """Flask uygulamasını oluşturur ve yapılandırır"""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    app.config.from_object(Config)
    
    # CORS'u etkinleştir
    CORS(app)
    
    # JWT'yi başlat
    JWTManager(app)
    
    # Veritabanını başlat
    init_db(app)
    
    # Ana route
    @app.route('/')
    def index():
        return 'Kişisel Finans Yönetim Sistemi API çalışıyor!'
    
    # Route'ları kaydet
    app.register_blueprint(auth_bp, url_prefix='/')  # Auth route'ları ana URL'de olsun
    app.register_blueprint(transaction_bp, url_prefix='/transactions')
    app.register_blueprint(category_bp, url_prefix='/categories')
    
    return app 