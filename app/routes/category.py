from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import db, Category

category_bp = Blueprint('category', __name__)

@category_bp.route('/', methods=['GET'])
@jwt_required()
def get_categories():
    """Tüm kategorileri listele"""
    categories = Category.query.all()
    return jsonify([category.to_dict() for category in categories]), 200

@category_bp.route('/', methods=['POST'])
@jwt_required()
def create_category():
    """Yeni kategori oluştur"""
    data = request.get_json()
    
    # Kategori adı kontrolü
    if Category.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Bu kategori adı zaten kullanımda'}), 400
    
    category = Category(
        name=data['name'],
        description=data.get('description', ''),
        type=data['type'],
        color=data.get('color', '#000000'),
        icon=data.get('icon', 'default')
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify(category.to_dict()), 201

@category_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    """Kategori güncelle"""
    category = Category.query.get(category_id)
    
    if not category:
        return jsonify({'error': 'Kategori bulunamadı'}), 404
    
    data = request.get_json()
    
    # İsim değişikliği varsa kontrol et
    if 'name' in data and data['name'] != category.name:
        if Category.query.filter_by(name=data['name']).first():
            return jsonify({'error': 'Bu kategori adı zaten kullanımda'}), 400
        category.name = data['name']
    
    # Diğer alanları güncelle
    if 'description' in data:
        category.description = data['description']
    if 'type' in data:
        category.type = data['type']
    if 'color' in data:
        category.color = data['color']
    if 'icon' in data:
        category.icon = data['icon']
    
    db.session.commit()
    
    return jsonify(category.to_dict()), 200

@category_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    """Kategori sil"""
    category = Category.query.get(category_id)
    
    if not category:
        return jsonify({'error': 'Kategori bulunamadı'}), 404
    
    # Kategoriye ait işlem var mı kontrol et
    if category.transactions:
        return jsonify({
            'error': 'Bu kategoriye ait işlemler var. Önce işlemleri başka bir kategoriye taşıyın.'
        }), 400
    
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({'message': 'Kategori başarıyla silindi'}), 200

@category_bp.route('/<int:category_id>/transactions', methods=['GET'])
@jwt_required()
def get_category_transactions(category_id):
    """Kategoriye ait işlemleri listele"""
    category = Category.query.get(category_id)
    
    if not category:
        return jsonify({'error': 'Kategori bulunamadı'}), 404
    
    transactions = [t.to_dict() for t in category.transactions]
    
    return jsonify({
        'category': category.to_dict(),
        'transactions': transactions,
        'total_amount': sum(t['amount'] for t in transactions)
    }), 200 