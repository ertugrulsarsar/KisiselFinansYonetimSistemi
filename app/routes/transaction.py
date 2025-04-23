from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Transaction, Category
from datetime import datetime

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/', methods=['GET'])
@jwt_required()
def get_transactions():
    """Kullanıcının işlemlerini listele"""
    current_user_id = get_jwt_identity()
    
    # Filtreleme parametreleri
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category_id = request.args.get('category_id')
    transaction_type = request.args.get('type')
    
    # Temel sorgu
    query = Transaction.query.filter_by(user_id=current_user_id)
    
    # Filtreleri uygula
    if start_date:
        query = query.filter(Transaction.transaction_date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Transaction.transaction_date <= datetime.strptime(end_date, '%Y-%m-%d'))
    if category_id:
        query = query.filter_by(category_id=category_id)
    if transaction_type:
        query = query.filter_by(transaction_type=transaction_type)
    
    # Tarihe göre sırala
    transactions = query.order_by(Transaction.transaction_date.desc()).all()
    
    return jsonify([t.to_dict() for t in transactions]), 200

@transaction_bp.route('/', methods=['POST'])
@jwt_required()
def create_transaction():
    """Yeni işlem oluştur"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Kategori kontrolü
    category = Category.query.get(data['category_id'])
    if not category:
        return jsonify({'error': 'Geçersiz kategori'}), 400
    
    # İşlem oluştur
    transaction = Transaction(
        user_id=current_user_id,
        category_id=data['category_id'],
        amount=data['amount'],
        description=data.get('description', ''),
        transaction_type=data['transaction_type'],
        transaction_date=datetime.strptime(data['transaction_date'], '%Y-%m-%d')
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify(transaction.to_dict()), 201

@transaction_bp.route('/<int:transaction_id>', methods=['PUT'])
@jwt_required()
def update_transaction(transaction_id):
    """İşlem güncelle"""
    current_user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user_id).first()
    
    if not transaction:
        return jsonify({'error': 'İşlem bulunamadı'}), 404
    
    data = request.get_json()
    
    # Kategori kontrolü
    if 'category_id' in data:
        category = Category.query.get(data['category_id'])
        if not category:
            return jsonify({'error': 'Geçersiz kategori'}), 400
        transaction.category_id = data['category_id']
    
    # Diğer alanları güncelle
    if 'amount' in data:
        transaction.amount = data['amount']
    if 'description' in data:
        transaction.description = data['description']
    if 'transaction_type' in data:
        transaction.transaction_type = data['transaction_type']
    if 'transaction_date' in data:
        transaction.transaction_date = datetime.strptime(data['transaction_date'], '%Y-%m-%d')
    
    db.session.commit()
    
    return jsonify(transaction.to_dict()), 200

@transaction_bp.route('/<int:transaction_id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(transaction_id):
    """İşlem sil"""
    current_user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user_id).first()
    
    if not transaction:
        return jsonify({'error': 'İşlem bulunamadı'}), 404
    
    db.session.delete(transaction)
    db.session.commit()
    
    return jsonify({'message': 'İşlem başarıyla silindi'}), 200

@transaction_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    """İşlem özeti"""
    current_user_id = get_jwt_identity()
    
    # Toplam gelir
    total_income = db.session.query(db.func.sum(Transaction.amount))\
        .filter_by(user_id=current_user_id, transaction_type='income')\
        .scalar() or 0
    
    # Toplam gider
    total_expense = db.session.query(db.func.sum(Transaction.amount))\
        .filter_by(user_id=current_user_id, transaction_type='expense')\
        .scalar() or 0
    
    # Kategori bazlı özet
    category_summary = db.session.query(
        Category.name,
        db.func.sum(Transaction.amount).label('total')
    ).join(Transaction)\
     .filter(Transaction.user_id == current_user_id)\
     .group_by(Category.name)\
     .all()
    
    return jsonify({
        'total_income': float(total_income),
        'total_expense': float(total_expense),
        'balance': float(total_income - total_expense),
        'category_summary': [{
            'category': name,
            'total': float(total)
        } for name, total in category_summary]
    }), 200 