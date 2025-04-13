from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from app.models import Transaction, Budget, Goal, Category, User
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func
import random
from app.forms import TransactionForm, ChangePasswordForm
from dateutil.relativedelta import relativedelta

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    # Son 5 işlemi al
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.date.desc())\
        .limit(5)\
        .all()
    
    # Son 6 ayın verilerini al
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    # Aylık gelir ve gider verilerini al
    monthly_data = []
    current_date = start_date
    while current_date <= end_date:
        month_income = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.type == 'income',
            Transaction.date >= current_date,
            Transaction.date < current_date + timedelta(days=30)
        ).with_entities(func.sum(Transaction.amount)).scalar() or 0
        
        month_expense = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.type == 'expense',
            Transaction.date >= current_date,
            Transaction.date < current_date + timedelta(days=30)
        ).with_entities(func.sum(Transaction.amount)).scalar() or 0
        
        monthly_data.append({
            'month': current_date.strftime('%B'),
            'income': month_income,
            'expense': month_expense
        })
        
        current_date += timedelta(days=30)
    
    # Toplam gelir ve gideri hesapla
    total_income = Transaction.query.filter_by(
        user_id=current_user.id,
        type='income'
    ).with_entities(func.sum(Transaction.amount)).scalar() or 0

    total_expense = Transaction.query.filter_by(
        user_id=current_user.id,
        type='expense'
    ).with_entities(func.sum(Transaction.amount)).scalar() or 0
    
    # Net miktarı hesapla
    net_amount = total_income - total_expense
    
    # Bütçe verilerini al
    budgets = Budget.query.filter_by(user_id=current_user.id).all()
    budget_data = []
    budget_labels = []
    budget_colors = []
    
    for budget in budgets:
        # Bütçe kategorisine göre işlemleri filtrele
        start_date = datetime.now().replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        spent = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.category == budget.category,
            Transaction.type == 'expense',
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).with_entities(func.sum(Transaction.amount)).scalar() or 0
        
        # Bütçe nesnesine spent özelliğini ekle
        budget.spent = spent
        
        budget_data.append({
            'category': budget.category.name,  # Category nesnesinin name özelliğini al
            'amount': budget.amount,
            'spent': spent,
            'remaining': budget.amount - spent
        })
        budget_labels.append(budget.category.name)
        budget_colors.append(f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.7)')
    
    # Hedef verilerini al
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    
    return render_template('index.html',
                         title='Ana Sayfa',
                         transactions=transactions,
                         budgets=budgets,
                         budget_data=budget_data,
                         budget_labels=budget_labels,
                         budget_colors=budget_colors,
                         goals=goals,
                         total_income=total_income,
                         total_expense=total_expense,
                         net_amount=net_amount,
                         monthly_data=monthly_data)

@bp.route('/transactions')
@login_required
def transactions():
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.date.desc())\
        .all()
    return render_template('transactions.html', title='İşlemler', transactions=transactions)

@bp.route('/budgets')
@login_required
def budgets():
    budgets = Budget.query.filter_by(user_id=current_user.id).all()
    for budget in budgets:
        spent = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.category == budget.category,
            Transaction.type == 'expense',
            Transaction.date >= datetime.now().replace(day=1),
            Transaction.date <= datetime.now()
        ).with_entities(func.sum(Transaction.amount)).scalar() or 0
        budget.spent = spent
    return render_template('budgets.html', title='Bütçeler', budgets=budgets)

@bp.route('/goals')
@login_required
def goals():
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    return render_template('goals.html', title='Hedefler', goals=goals, min=min)

@bp.route('/reports')
@login_required
def reports():
    return render_template('reports.html', title='Raporlar')

@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Profil')

@bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html', title='Ayarlar')

@bp.route('/add_transaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
    form = TransactionForm()
    
    # GET isteği için kategorileri yükle
    if request.method == 'GET':
        categories = Category.query.filter_by(type='expense').all()
        form.category_id.choices = [(c.id, c.name) for c in categories]
    
    # POST isteği için form doğrulama
    if form.validate_on_submit():
        transaction = Transaction(
            amount=form.amount.data,
            description=form.description.data,
            category_id=form.category_id.data,
            type=form.type.data,
            date=form.date.data,
            user_id=current_user.id
        )
        db.session.add(transaction)
        db.session.commit()
        flash('İşlem başarıyla eklendi.', 'success')
        return redirect(url_for('main.transactions'))
    
    return render_template('add_transaction.html', title='Yeni İşlem', form=form)

@bp.route('/add_budget', methods=['GET', 'POST'])
@login_required
def add_budget():
    if request.method == 'POST':
        # Bütçe ekleme işlemleri
        pass
    return render_template('add_budget.html', title='Yeni Bütçe')

@bp.route('/add_goal', methods=['GET', 'POST'])
@login_required
def add_goal():
    if request.method == 'POST':
        # Hedef ekleme işlemleri
        pass
    return render_template('add_goal.html', title='Yeni Hedef')

@bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        # Profil güncelleme işlemleri
        pass
    return redirect(url_for('main.profile'))

@bp.route('/update_settings', methods=['POST'])
@login_required
def update_settings():
    if request.method == 'POST':
        # Ayarları güncelleme işlemleri
        pass
    return redirect(url_for('main.settings'))

@bp.route('/update_notification_settings', methods=['POST'])
@login_required
def update_notification_settings():
    if request.method == 'POST':
        # Bildirim ayarlarını güncelleme işlemleri
        pass
    return redirect(url_for('main.settings'))

@bp.route('/transactions/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    if transaction.user_id != current_user.id:
        abort(403)
    form = TransactionForm()
    if form.validate_on_submit():
        transaction.amount = form.amount.data
        transaction.description = form.description.data
        transaction.category = form.category.data
        transaction.type = form.type.data
        transaction.date = form.date.data
        db.session.commit()
        flash('İşlem başarıyla güncellendi.', 'success')
        return redirect(url_for('main.transactions'))
    elif request.method == 'GET':
        form.amount.data = transaction.amount
        form.description.data = transaction.description
        form.category.data = transaction.category
        form.type.data = transaction.type
        form.date.data = transaction.date
    return render_template('edit_transaction.html', title='İşlem Düzenle', form=form)

@bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Şifreniz başarıyla değiştirildi.', 'success')
        else:
            flash('Mevcut şifreniz yanlış.', 'danger')
    return redirect(url_for('main.profile'))

@bp.route('/transactions/<int:id>/delete', methods=['POST'])
@login_required
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    if transaction.user_id != current_user.id:
        abort(403)
    db.session.delete(transaction)
    db.session.commit()
    flash('İşlem başarıyla silindi.', 'success')
    return redirect(url_for('main.transactions'))

@bp.route('/api/categories/<type>')
@login_required
def get_categories(type):
    categories = Category.query.filter_by(type=type).all()
    return jsonify([{'id': c.id, 'name': c.name} for c in categories]) 