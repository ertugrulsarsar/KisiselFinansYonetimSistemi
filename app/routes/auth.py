from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from app.models import db, User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Yeni kullanıcı kaydı"""
    data = request.get_json()
    
    # Kullanıcı adı ve email kontrolü
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Bu kullanıcı adı zaten kullanımda'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Bu email adresi zaten kullanımda'}), 400
    
    # Yeni kullanıcı oluştur
    user = User(
        username=data['username'],
        email=data['email'],
        first_name=data.get('first_name'),
        last_name=data.get('last_name')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'Kullanıcı başarıyla oluşturuldu', 'user_id': user.id}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Kullanıcı girişi"""
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
    
    return jsonify({'error': 'Geçersiz kullanıcı adı veya şifre'}), 401

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """Kullanıcı profil bilgileri"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
    
    return jsonify(user.to_dict()), 200

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Kullanıcı profil güncelleme"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
    
    data = request.get_json()
    
    # Güvenli güncelleme
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'email' in data:
        if User.query.filter(User.email == data['email'], User.id != current_user_id).first():
            return jsonify({'error': 'Bu email adresi zaten kullanımda'}), 400
        user.email = data['email']
    if 'password' in data:
        user.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({'message': 'Profil güncellendi', 'user': user.to_dict()}), 200 