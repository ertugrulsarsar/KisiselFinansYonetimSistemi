from datetime import datetime
from . import db
from passlib.hash import pbkdf2_sha256

class User(db.Model):
    """Kullanıcı modeli"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # İlişkiler
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    budgets = db.relationship('Budget', backref='user', lazy=True)

    def set_password(self, password):
        """Şifreyi hashleyerek kaydeder"""
        self.password_hash = pbkdf2_sha256.hash(password)

    def check_password(self, password):
        """Şifre doğrulaması yapar"""
        return pbkdf2_sha256.verify(password, self.password_hash)

    def to_dict(self):
        """Kullanıcı bilgilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 