from datetime import datetime
from . import db

class Budget(db.Model):
    """Bütçe modeli"""
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        """Bütçe bilgilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'amount': float(self.amount),
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def calculate_spent_amount(self):
        """Bu bütçe için harcanan toplam tutarı hesaplar"""
        from .transaction import Transaction
        spent = db.session.query(db.func.sum(Transaction.amount))\
            .filter(
                Transaction.user_id == self.user_id,
                Transaction.category_id == self.category_id,
                Transaction.transaction_type == 'expense',
                Transaction.transaction_date.between(self.start_date, self.end_date)
            ).scalar()
        return float(spent) if spent else 0.0

    def get_remaining_amount(self):
        """Kalan bütçe tutarını hesaplar"""
        spent = self.calculate_spent_amount()
        return float(self.amount) - spent 