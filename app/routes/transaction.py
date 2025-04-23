from flask import Blueprint, request, jsonify, render_template, url_for, redirect, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Transaction, Category
from datetime import datetime
from enum import Enum
from marshmallow import Schema, fields, ValidationError
from sqlalchemy import extract

class TransactionType(Enum):
    INCOME = 'income'
    EXPENSE = 'expense'

class TransactionSchema(Schema):
    category_id = fields.Integer(required=True)
    amount = fields.Float(required=True)
    description = fields.String()
    transaction_type = fields.String(required=True, validate=lambda x: x in [t.value for t in TransactionType])
    transaction_date = fields.Date(required=True)

transaction_bp = Blueprint('transaction', __name__)

def validate_date_format(date_str):
    """Tarih formatını kontrol et"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None

@transaction_bp.errorhandler(ValidationError)
def handle_validation_error(error):
    """Doğrulama hatalarını yönet"""
    return jsonify({'error': str(error.messages)}), 400

@transaction_bp.route('/')
@jwt_required()
def index():
    """İşlemler sayfasını göster"""
    return redirect(url_for('transaction.get_transactions'))

@transaction_bp.route('/list')
@jwt_required()
def get_transactions():
    """Kullanıcının işlemlerini listele"""
    user_id = get_jwt_identity()
    
    # Query parametrelerini al
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category_id = request.args.get('category_id')
    transaction_type = request.args.get('type')
    
    # Base query
    query = Transaction.query.filter_by(user_id=user_id)
    
    # Filtreleri uygula
    if start_date:
        query = query.filter(Transaction.transaction_date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Transaction.transaction_date <= datetime.strptime(end_date, '%Y-%m-%d'))
    if category_id:
        query = query.filter_by(category_id=category_id)
    if transaction_type:
        query = query.filter_by(transaction_type=transaction_type)
    
    transactions = query.order_by(Transaction.transaction_date.desc()).all()
    
    # Kategorileri getir
    categories = Category.query.filter_by(user_id=user_id).all()
    
    # API isteği mi yoksa sayfa isteği mi?
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify([t.to_dict() for t in transactions]), 200
    else:
        return render_template('transactions.html', 
                             transactions=transactions,
                             categories=categories)

@transaction_bp.route('/', methods=['POST'])
@jwt_required()
def create_transaction():
    """Yeni bir işlem oluşturur"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Kategori kontrolü
    category = Category.query.get(data.get('category_id'))
    if not category or category.user_id != user_id:
        return jsonify({'error': 'Geçersiz kategori'}), 400
        
    transaction = Transaction(
        amount=data['amount'],
        type=data['type'],
        description=data.get('description', ''),
        date=datetime.strptime(data['date'], '%Y-%m-%d'),
        category_id=data['category_id'],
        user_id=user_id
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify(transaction.to_dict()), 201

@transaction_bp.route('/<int:transaction_id>')
@jwt_required()
def get_transaction(transaction_id):
    """İşlem detaylarını getir"""
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=get_jwt_identity()).first()
    
    if not transaction:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'İşlem bulunamadı'}), 404
        else:
            flash('İşlem bulunamadı', 'danger')
            return redirect(url_for('transaction.get_transactions'))
            
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(transaction.to_dict()), 200
    else:
        return render_template('transaction_detail.html', transaction=transaction)

@transaction_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_transaction(id):
    """Belirtilen işlemi günceller"""
    user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(id=id, user_id=user_id).first()
    
    if not transaction:
        return jsonify({'error': 'İşlem bulunamadı'}), 404
        
    data = request.get_json()
    
    # Kategori kontrolü
    if 'category_id' in data:
        category = Category.query.get(data['category_id'])
        if not category or category.user_id != user_id:
            return jsonify({'error': 'Geçersiz kategori'}), 400
    
    # Alanları güncelle
    for key, value in data.items():
        if key == 'date':
            setattr(transaction, key, datetime.strptime(value, '%Y-%m-%d'))
        else:
            setattr(transaction, key, value)
    
    db.session.commit()
    return jsonify(transaction.to_dict())

@transaction_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(id):
    """Belirtilen işlemi siler"""
    user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(id=id, user_id=user_id).first()
    
    if not transaction:
        return jsonify({'error': 'İşlem bulunamadı'}), 404
        
    db.session.delete(transaction)
    db.session.commit()
    
    return jsonify({'message': 'İşlem başarıyla silindi'})

@transaction_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    """İşlem özetini döndürür"""
    user_id = get_jwt_identity()
    
    # Query parametrelerini al
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    # Aylık işlemleri getir
    transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        extract('year', Transaction.transaction_date) == year,
        extract('month', Transaction.transaction_date) == month
    ).all()
    
    # Toplam gelir ve giderleri hesapla
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expense = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    
    # Kategori bazlı özet
    category_summary = {}
    for t in transactions:
        category_name = t.category.name
        if category_name not in category_summary:
            category_summary[category_name] = {'income': 0, 'expense': 0}
        category_summary[category_name][t.transaction_type] += t.amount
    
    return jsonify({
        'total_income': total_income,
        'total_expense': total_expense,
        'net': total_income - total_expense,
        'category_summary': category_summary
    }) 