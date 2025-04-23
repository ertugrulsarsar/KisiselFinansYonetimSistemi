from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.models import init_db
from app.routes import api_bp
from config import Config

def create_app():
    """Flask uygulamasını oluşturur ve yapılandırır"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # CORS'u etkinleştir
    CORS(app)
    
    # JWT'yi başlat
    JWTManager(app)
    
    # Veritabanını başlat
    init_db(app)
    
    # API route'larını kaydet
    app.register_blueprint(api_bp)
    
    @app.route('/')
    def index():
        return 'Kişisel Finans Yönetim Sistemi API çalışıyor!'
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
