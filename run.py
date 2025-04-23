from flask import Flask
from app.models import init_db
from config import Config

def create_app():
    """Flask uygulamasını oluşturur ve yapılandırır"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Veritabanını başlat
    init_db(app)
    
    @app.route('/')
    def index():
        return 'Kişisel Finans Yönetim Sistemi çalışıyor!'
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
