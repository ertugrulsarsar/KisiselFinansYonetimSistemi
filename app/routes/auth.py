from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from app.models import db, User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.services import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Yeni kullanıcı kaydı"""
    data = request.get_json()
    user, message = AuthService.register_user(data)
    
    if user:
        return jsonify({
            'message': message,
            'user_id': user.id
        }), 201
    return jsonify({'error': message}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    """Kullanıcı girişi"""
    data = request.get_json()
    result, message = AuthService.login_user(data['username'], data['password'])
    
    if result:
        return jsonify({
            'access_token': result['token'],
            'user': result['user'].to_dict()
        }), 200
    return jsonify({'error': message}), 401

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
    data = request.get_json()
    
    user, message = AuthService.update_user_profile(current_user_id, data)
    
    if user:
        return jsonify({
            'message': message,
            'user': user.to_dict()
        }), 200
    return jsonify({'error': message}), 400

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password_request():
    """Şifre sıfırlama isteği"""
    data = request.get_json()
    user, message = AuthService.reset_password_request(data['email'])
    
    if user:
        return jsonify({'message': message}), 200
    return jsonify({'error': message}), 400 