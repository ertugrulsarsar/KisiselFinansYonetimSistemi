from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    budgets = db.relationship('Budget', backref='user', lazy='dynamic')
    goals = db.relationship('Goal', backref='user', lazy='dynamic')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' veya 'expense'
    transactions = db.relationship('Transaction', backref='category', lazy='dynamic')
    budgets = db.relationship('Budget', backref='category', lazy='dynamic')

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), nullable=False)  # 'income' veya 'expense'
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'category': self.category.name,
            'description': self.description,
            'type': self.type,
            'date': self.date.isoformat()
        }

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    spent_amount = db.Column(db.Float, default=0)
    period = db.Column(db.String(10), nullable=False)  # 'daily', 'weekly', 'monthly', 'yearly'
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def __repr__(self):
        return f'<Budget {self.category.name}>'

    def get_remaining_amount(self):
        # Bu kategorideki toplam harcamayı hesapla
        total_spent = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == self.user_id,
            Transaction.category_id == self.category_id,
            Transaction.type == 'expense',
            Transaction.date >= self.start_date,
            Transaction.date <= self.end_date
        ).scalar() or 0

        return self.amount - total_spent

    def get_usage_percentage(self):
        total_spent = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == self.user_id,
            Transaction.category_id == self.category_id,
            Transaction.type == 'expense',
            Transaction.date >= self.start_date,
            Transaction.date <= self.end_date
        ).scalar() or 0

        return (total_spent / self.amount) * 100 if self.amount > 0 else 0

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0)
    deadline = db.Column(db.DateTime, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Goal {self.title}>'

    def get_progress_percentage(self):
        return (self.current_amount / self.target_amount) * 100 if self.target_amount > 0 else 0

    def update_status(self):
        if self.current_amount >= self.target_amount:
            self.is_completed = True
        elif self.deadline < datetime.utcnow():
            self.is_completed = False
        db.session.commit() 