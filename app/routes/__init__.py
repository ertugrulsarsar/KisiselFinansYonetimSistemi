from flask import Blueprint
from .auth import auth_bp
from .transaction import transaction_bp
from .category import category_bp

# API Blueprint'i oluştur
api_bp = Blueprint('api', __name__)

# API route'larını kaydet
api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(transaction_bp, url_prefix='/transactions')
api_bp.register_blueprint(category_bp, url_prefix='/categories')

# Blueprint'leri dışa aktar
__all__ = ['api_bp', 'auth_bp', 'transaction_bp', 'category_bp'] 