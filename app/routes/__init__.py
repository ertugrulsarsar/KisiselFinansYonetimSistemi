# Bu dosya routes paketini tanımlar 
from flask import Blueprint
from .main import bp as main_bp
from .transactions import bp as transactions_bp
from .budgets import bp as budgets_bp
from .goals import bp as goals_bp

# Ana blueprint'i oluştur
bp = Blueprint('routes', __name__)

# Alt blueprint'leri ana blueprint'e kaydet
bp.register_blueprint(main_bp)
bp.register_blueprint(transactions_bp, url_prefix='/transactions')
bp.register_blueprint(budgets_bp, url_prefix='/budgets')
bp.register_blueprint(goals_bp, url_prefix='/goals') 