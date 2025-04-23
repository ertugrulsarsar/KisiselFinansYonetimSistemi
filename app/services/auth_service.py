from app.models import db, User
from flask_jwt_extended import create_access_token
from datetime import timedelta
import re

class AuthService:
    @staticmethod
    def validate_password(password):
        """Şifre geçerliliğini kontrol eder"""
        if len(password) < 8:
            return False, "Şifre en az 8 karakter olmalıdır"
        if not re.search(r"[A-Z]", password):
            return False, "Şifre en az bir büyük harf içermelidir"
        if not re.search(r"[a-z]", password):
            return False, "Şifre en az bir küçük harf içermelidir"
        if not re.search(r"\d", password):
            return False, "Şifre en az bir rakam içermelidir"
        return True, "Şifre geçerli"

    @staticmethod
    def validate_email(email):
        """Email geçerliliğini kontrol eder"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Geçersiz email formatı"
        return True, "Email geçerli"

    @staticmethod
    def register_user(data):
        """Yeni kullanıcı kaydı yapar"""
        # Veri doğrulama
        if not all(key in data for key in ['username', 'email', 'password']):
            return None, "Eksik bilgi"

        # Email ve şifre kontrolü
        email_valid, email_msg = AuthService.validate_email(data['email'])
        if not email_valid:
            return None, email_msg

        password_valid, password_msg = AuthService.validate_password(data['password'])
        if not password_valid:
            return None, password_msg

        # Kullanıcı adı ve email kontrolü
        if User.query.filter_by(username=data['username']).first():
            return None, "Bu kullanıcı adı zaten kullanımda"
        if User.query.filter_by(email=data['email']).first():
            return None, "Bu email adresi zaten kullanımda"

        try:
            user = User(
                username=data['username'],
                email=data['email'],
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', '')
            )
            user.set_password(data['password'])
            
            db.session.add(user)
            db.session.commit()
            return user, "Kullanıcı başarıyla oluşturuldu"
        except Exception as e:
            db.session.rollback()
            return None, f"Kayıt işlemi başarısız: {str(e)}"

    @staticmethod
    def login_user(username, password):
        """Kullanıcı girişi yapar"""
        try:
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                if not user.is_active:
                    return None, "Hesabınız aktif değil"
                
                access_token = create_access_token(
                    identity=user.id,
                    expires_delta=timedelta(hours=24)
                )
                return {'token': access_token, 'user': user}, "Giriş başarılı"
            return None, "Geçersiz kullanıcı adı veya şifre"
        except Exception as e:
            return None, f"Giriş işlemi başarısız: {str(e)}"

    @staticmethod
    def update_user_profile(user_id, data):
        """Kullanıcı profilini günceller"""
        try:
            user = User.query.get(user_id)
            if not user:
                return None, "Kullanıcı bulunamadı"

            if 'email' in data:
                email_valid, email_msg = AuthService.validate_email(data['email'])
                if not email_valid:
                    return None, email_msg
                
                existing_user = User.query.filter(
                    User.email == data['email'],
                    User.id != user_id
                ).first()
                if existing_user:
                    return None, "Bu email adresi zaten kullanımda"
                user.email = data['email']

            if 'password' in data:
                password_valid, password_msg = AuthService.validate_password(data['password'])
                if not password_valid:
                    return None, password_msg
                user.set_password(data['password'])

            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']

            db.session.commit()
            return user, "Profil başarıyla güncellendi"
        except Exception as e:
            db.session.rollback()
            return None, f"Güncelleme işlemi başarısız: {str(e)}"

    @staticmethod
    def reset_password_request(email):
        """Şifre sıfırlama isteği oluşturur"""
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                return None, "Bu email adresi ile kayıtlı kullanıcı bulunamadı"

            # TODO: Şifre sıfırlama token'ı oluştur ve email gönder
            # Bu kısım email servisi entegrasyonu sonrası implement edilecek
            
            return user, "Şifre sıfırlama talimatları email adresinize gönderildi"
        except Exception as e:
            return None, f"Şifre sıfırlama isteği başarısız: {str(e)}" 