from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user, login_user, logout_user
from app import db
from app.models import User, Transaction
from app.forms import LoginForm, RegistrationForm, TransactionForm
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)
transactions = Blueprint('transactions', __name__)

@main.route('/')
@login_required
def index():
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.date.desc())\
        .limit(5)\
        .all()
    
    total_income = Transaction.query.filter_by(
        user_id=current_user.id,
        type='income'
    ).with_entities(db.func.sum(Transaction.amount)).scalar() or 0
    
    total_expense = Transaction.query.filter_by(
        user_id=current_user.id,
        type='expense'
    ).with_entities(db.func.sum(Transaction.amount)).scalar() or 0
    
    form = TransactionForm()
    return render_template('index.html',
                         recent_transactions=recent_transactions,
                         total_income=total_income,
                         total_expense=total_expense,
                         form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Geçersiz kullanıcı adı veya şifre', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Giriş', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Tebrikler, başarıyla kayıt oldunuz!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Kayıt Ol', form=form)

@main.route('/transactions/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    form = TransactionForm()
    if form.validate_on_submit():
        transaction = Transaction(
            type=form.type.data,
            amount=form.amount.data,
            category=form.category.data,
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(transaction)
        db.session.commit()
        flash('İşlem başarıyla eklendi!', 'success')
        return redirect(url_for('main.index'))
    return render_template('transactions/add.html', form=form)

@main.route('/transactions/list')
@login_required
def list_transactions():
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.date.desc())\
        .all()
    return render_template('transactions/list.html', transactions=transactions)

@transactions.route('/api/summary')
@login_required
def get_summary():
    # Son 30 günlük özet
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= thirty_days_ago
    ).all()
    
    summary = {
        'total_income': sum(t.amount for t in transactions if t.type == 'income'),
        'total_expense': sum(t.amount for t in transactions if t.type == 'expense'),
        'categories': {}
    }
    
    for t in transactions:
        if t.type == 'expense':
            if t.category not in summary['categories']:
                summary['categories'][t.category] = 0
            summary['categories'][t.category] += t.amount
    
    return jsonify(summary)

@main.route('/transactions/edit/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.user_id != current_user.id:
        flash('Bu işlemi düzenleme yetkiniz yok.', 'danger')
        return redirect(url_for('main.index'))
    
    form = TransactionForm()
    if form.validate_on_submit():
        transaction.type = form.type.data
        transaction.amount = form.amount.data
        transaction.category = form.category.data
        transaction.description = form.description.data
        db.session.commit()
        flash('İşlem başarıyla güncellendi!', 'success')
        return redirect(url_for('main.list_transactions'))
    
    # Form alanlarını mevcut verilerle doldur
    form.type.data = transaction.type
    form.amount.data = transaction.amount
    form.category.data = transaction.category
    form.description.data = transaction.description
    
    return render_template('transactions/edit.html', form=form, transaction=transaction)

@main.route('/transactions/delete/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Yetkilendirme hatası'})
    
    try:
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Silme hatası: {str(e)}')
        return jsonify({'success': False, 'error': 'Veritabanı hatası'}) 