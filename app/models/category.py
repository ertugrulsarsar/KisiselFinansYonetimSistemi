from datetime import datetime
from . import db

class Category(db.Model):
    """İşlem kategorisi modeli"""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    type = db.Column(db.String(10), nullable=False)  # 'income' veya 'expense'
    color = db.Column(db.String(7))  # Örnek: #FF0000
    icon = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # İlişkiler
    transactions = db.relationship('Transaction', backref='category', lazy=True)

    def to_dict(self):
        """Kategori bilgilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'color': self.color,
            'icon': self.icon,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 