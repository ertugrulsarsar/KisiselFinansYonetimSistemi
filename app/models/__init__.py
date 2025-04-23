from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Veritabanı bağlantısını başlatır"""
    db.init_app(app)
    with app.app_context():
        db.create_all()

# Modelleri import et
from .user import User
from .transaction import Transaction
from .category import Category
from .budget import Budget

# Modelleri dışa aktar
__all__ = ['db', 'init_db', 'User', 'Transaction', 'Category', 'Budget'] 