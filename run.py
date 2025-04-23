from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.models import init_db
from app.routes import api_bp
from config import Config
import logging

def create_app():
    """Flask uygulamasını oluşturur ve yapılandırır"""
    # Loglama seviyesini ayarla
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    logger.info("CORS yapılandırılıyor...")
    CORS(app)
    
    logger.info("JWT başlatılıyor...")
    JWTManager(app)
    
    logger.info("Veritabanı başlatılıyor...")
    try:
        init_db(app)
        logger.info("Veritabanı başarıyla başlatıldı!")
    except Exception as e:
        logger.error(f"Veritabanı başlatılırken hata oluştu: {str(e)}")
        raise
    
    # Ana route
    @app.route('/')
    def index():
        return 'Kişisel Finans Yönetim Sistemi API çalışıyor!'
    
    logger.info("Route'lar kaydediliyor...")
    # Ana API blueprint'i kaydet
    app.register_blueprint(api_bp, url_prefix='/api')
    logger.info("Route'lar başarıyla kaydedildi!")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
