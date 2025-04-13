from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from app import db
from app.models import User, Transaction, Budget, Goal, Category
from sqlalchemy import func
import random
from app.forms import TransactionForm, ChangePasswordForm, BudgetForm, GoalForm

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    # Son işlemleri al
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.date.desc())\
        .limit(5).all()
    
    # Toplam gelir ve giderleri hesapla
    total_income = db.session.query(func.sum(Transaction.amount))\
        .filter(Transaction.user_id == current_user.id, Transaction.type == 'income')\
        .scalar() or 0
    
    total_expense = db.session.query(func.sum(Transaction.amount))\
        .filter(Transaction.user_id == current_user.id, Transaction.type == 'expense')\
        .scalar() or 0
    
    net_amount = total_income - total_expense
    
    # Aktif bütçeleri al
    budgets = Budget.query.filter(
        Budget.user_id == current_user.id,
        Budget.end_date >= datetime.now()
    ).all()
    
    # Aktif hedefleri al
    active_goals = Goal.query.filter(
        Goal.user_id == current_user.id,
        Goal.deadline >= datetime.now(),
        Goal.is_completed == False
    ).count()
    
    # Aylık verileri hazırla
    monthly_data = []
    for i in range(5, -1, -1):
        date = datetime.now() - relativedelta(months=i)
        month_income = db.session.query(func.sum(Transaction.amount))\
            .filter(Transaction.user_id == current_user.id,
                   Transaction.type == 'income',
                   func.extract('year', Transaction.date) == date.year,
                   func.extract('month', Transaction.date) == date.month)\
            .scalar() or 0
        
        month_expense = db.session.query(func.sum(Transaction.amount))\
            .filter(Transaction.user_id == current_user.id,
                   Transaction.type == 'expense',
                   func.extract('year', Transaction.date) == date.year,
                   func.extract('month', Transaction.date) == date.month)\
            .scalar() or 0
        
        monthly_data.append({
            'month': date.strftime('%B %Y'),
            'income': month_income,
            'expense': month_expense
        })
    
    # Kategori verilerini hazırla
    category_data = []
    categories = Category.query.filter_by(type='expense').all()
    for category in categories:
        total = db.session.query(func.sum(Transaction.amount))\
            .filter(Transaction.user_id == current_user.id,
                   Transaction.category_id == category.id,
                   Transaction.date >= datetime.now().replace(day=1))\
            .scalar() or 0
        if total > 0:
            category_data.append({
                'name': category.name,
                'amount': total
            })
    
    return render_template('index.html',
                         title='Ana Sayfa',
                         transactions=recent_transactions,
                         total_income=total_income,
                         total_expense=total_expense,
                         net_amount=net_amount,
                         budgets=budgets,
                         active_goals=active_goals,
                         monthly_data=monthly_data,
                         category_data=category_data)

@bp.route('/reports')
@login_required
def reports():
    return render_template('reports.html', title='Raporlar')

@bp.route('/api/reports/data')
@login_required
def get_report_data():
    period = request.args.get('period', 'monthly')
    today = datetime.now()
    
    if period == 'monthly':
        start_date = today.replace(day=1)
        labels = [(start_date + timedelta(days=i)).strftime('%d') for i in range(31)]
        transactions = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= start_date
        ).all()
    else:  # yearly
        start_date = today.replace(month=1, day=1)
        labels = [(start_date + relativedelta(months=i)).strftime('%B') for i in range(12)]
        transactions = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= start_date
        ).all()

    income_data = [0] * len(labels)
    expense_data = [0] * len(labels)
    category_data = {}
    total_income = 0
    total_expense = 0

    for transaction in transactions:
        if period == 'monthly':
            index = transaction.date.day - 1
        else:
            index = transaction.date.month - 1

        if transaction.type == 'income':
            income_data[index] += transaction.amount
            total_income += transaction.amount
        else:
            expense_data[index] += transaction.amount
            total_expense += transaction.amount

        if transaction.category not in category_data:
            category_data[transaction.category] = 0
        category_data[transaction.category] += transaction.amount

    trend_data = [income - expense for income, expense in zip(income_data, expense_data)]

    return jsonify({
        'labels': labels,
        'income_data': income_data,
        'expense_data': expense_data,
        'trend_data': trend_data,
        'category_data': category_data,
        'total_income': total_income,
        'total_expense': total_expense
    })

@bp.route('/transactions')
@login_required
def transactions():
    page = request.args.get('page', 1, type=int)
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .join(Category)\
        .order_by(Transaction.date.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('transactions.html', 
                         title='İşlemler',
                         transactions=transactions.items)

@bp.route('/transactions/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    form = TransactionForm()
    
    # Kategorileri al
    income_categories = Category.query.filter_by(type='income').all()
    expense_categories = Category.query.filter_by(type='expense').all()
    
    # Kategorileri JSON formatına dönüştür
    income_categories_json = [{'id': c.id, 'name': c.name} for c in income_categories]
    expense_categories_json = [{'id': c.id, 'name': c.name} for c in expense_categories]
    
    if request.method == 'GET':
        # Varsayılan değerleri ayarla
        form.type.data = 'expense'
        form.date.data = datetime.now()
        # Kategori seçeneklerini ayarla
        form.category_id.choices = [(c.id, c.name) for c in expense_categories]
    
    if form.validate_on_submit():
        try:
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
        except Exception as e:
            db.session.rollback()
            flash('İşlem eklenirken bir hata oluştu: ' + str(e), 'danger')
    
    return render_template('add_transaction.html', 
                         title='Yeni İşlem', 
                         form=form,
                         income_categories=income_categories_json,
                         expense_categories=expense_categories_json)

@bp.route('/transactions/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    if transaction.user_id != current_user.id:
        abort(403)
    
    form = TransactionForm(obj=transaction)
    if request.method == 'GET':
        categories = Category.query.filter_by(type='expense').all()
        form.category_id.choices = [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        transaction.amount = form.amount.data
        transaction.description = form.description.data
        transaction.category_id = form.category_id.data
        transaction.type = form.type.data
        transaction.date = form.date.data
        db.session.commit()
        flash('İşlem başarıyla güncellendi.', 'success')
        return redirect(url_for('main.transactions'))
    
    return render_template('edit_transaction.html', title='İşlem Düzenle', form=form, transaction=transaction)

@bp.route('/delete_transaction/<int:id>', methods=['POST'])
@login_required
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    if transaction.user_id != current_user.id:
        abort(403)
    
    db.session.delete(transaction)
    db.session.commit()
    flash('İşlem başarıyla silindi.', 'success')
    return redirect(url_for('main.transactions'))

@bp.route('/budgets')
@login_required
def budgets():
    budgets = Budget.query.filter_by(user_id=current_user.id).order_by(Budget.end_date.asc()).all()
    return render_template('budgets.html', title='Bütçeler', budgets=budgets)

@bp.route('/budgets/add', methods=['GET', 'POST'])
@login_required
def add_budget():
    form = BudgetForm()
    if request.method == 'GET':
        categories = Category.query.filter_by(type='expense').all()
        form.category_id.choices = [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        budget = Budget(
            amount=form.amount.data,
            category_id=form.category_id.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            user_id=current_user.id
        )
        db.session.add(budget)
        db.session.commit()
        flash('Bütçe başarıyla eklendi.', 'success')
        return redirect(url_for('main.budgets'))
    
    return render_template('add_budget.html', title='Yeni Bütçe', form=form)

@bp.route('/goals')
@login_required
def goals():
    goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.deadline.asc()).all()
    return render_template('goals.html', title='Hedefler', goals=goals)

@bp.route('/goals/add', methods=['GET', 'POST'])
@login_required
def add_goal():
    form = GoalForm()
    if form.validate_on_submit():
        goal = Goal(
            title=form.title.data,
            target_amount=form.target_amount.data,
            current_amount=form.current_amount.data,
            deadline=form.deadline.data,
            user_id=current_user.id
        )
        db.session.add(goal)
        db.session.commit()
        flash('Hedef başarıyla eklendi.', 'success')
        return redirect(url_for('main.goals'))
    return render_template('add_goal.html', title='Yeni Hedef', form=form)

@bp.route('/goals/<int:id>', methods=['GET', 'POST', 'DELETE'])
@login_required
def goal(id):
    goal = Goal.query.get_or_404(id)
    if goal.user_id != current_user.id:
        abort(403)
    
    if request.method == 'DELETE':
        db.session.delete(goal)
        db.session.commit()
        return '', 204
    
    form = GoalForm(obj=goal)
    if form.validate_on_submit():
        goal.title = form.title.data
        goal.target_amount = form.target_amount.data
        goal.current_amount = form.current_amount.data
        goal.deadline = form.deadline.data
        db.session.commit()
        flash('Hedef başarıyla güncellendi.', 'success')
        return redirect(url_for('main.goals'))
    
    return render_template('edit_goal.html', title='Hedef Düzenle', form=form, goal=goal)

@bp.route('/budgets/<int:id>', methods=['GET', 'POST', 'DELETE'])
@login_required
def budget(id):
    budget = Budget.query.get_or_404(id)
    if budget.user_id != current_user.id:
        abort(403)
    
    if request.method == 'DELETE':
        db.session.delete(budget)
        db.session.commit()
        return '', 204
    
    form = BudgetForm(obj=budget)
    if request.method == 'GET':
        categories = Category.query.filter_by(type='expense').all()
        form.category_id.choices = [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        budget.amount = form.amount.data
        budget.category_id = form.category_id.data
        budget.start_date = form.start_date.data
        budget.end_date = form.end_date.data
        db.session.commit()
        flash('Bütçe başarıyla güncellendi.', 'success')
        return redirect(url_for('main.budgets'))
    
    return render_template('edit_budget.html', title='Bütçe Düzenle', form=form, budget=budget)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password_hash, form.current_password.data):
            current_user.password_hash = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash('Şifreniz başarıyla güncellendi.', 'success')
            return redirect(url_for('main.profile'))
        else:
            flash('Mevcut şifreniz yanlış.', 'danger')
    
    return render_template('profile.html', title='Profil', form=form) 