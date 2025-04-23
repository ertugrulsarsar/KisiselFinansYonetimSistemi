from flask import Blueprint
from .auth import auth_bp
from .transaction import transaction_bp
from .category import category_bp

# Ana API Blueprint'i oluştur
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Alt route'ları kaydet
api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(transaction_bp, url_prefix='/transactions')
api_bp.register_blueprint(category_bp, url_prefix='/categories') 