from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, abort
from flask_login import login_required, current_user, login_user, logout_user
from app import db
from app.models import User, Transaction, Budget, Goal
from app.forms import LoginForm, RegistrationForm, TransactionForm, BudgetForm, GoalForm
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
from sqlalchemy import func

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)
transactions = Blueprint('transactions', __name__)

@main.route('/')
@main.route('/index')
@login_required
def index():
    # Son 5 işlemi getir
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.date.desc())\
        .limit(5).all()
    
    # Toplam gelir ve gider
    total_income = db.session.query(func.sum(Transaction.amount))\
        .filter(Transaction.user_id == current_user.id,
                Transaction.type == 'income').scalar() or 0
    
    total_expense = db.session.query(func.sum(Transaction.amount))\
        .filter(Transaction.user_id == current_user.id,
                Transaction.type == 'expense').scalar() or 0
    
    # Aktif bütçeler
    active_budgets = Budget.query.filter_by(user_id=current_user.id)\
        .filter(Budget.end_date >= datetime.now().date())\
        .all()
    
    # Aktif hedefler
    active_goals = Goal.query.filter_by(user_id=current_user.id)\
        .filter(Goal.status == 'active')\
        .all()
    
    return render_template('index.html',
                         recent_transactions=recent_transactions,
                         total_income=total_income,
                         total_expense=total_expense,
                         active_budgets=active_budgets,
                         active_goals=active_goals)

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

@main.route('/transactions')
@login_required
def list_transactions():
    page = request.args.get('page', 1, type=int)
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.date.desc())\
        .paginate(page=page, per_page=10)
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
            date=form.date.data,
            user_id=current_user.id
        )
        db.session.add(transaction)
        db.session.commit()
        flash('İşlem başarıyla eklendi.', 'success')
        return redirect(url_for('main.list_transactions'))
    return render_template('transactions/add.html', form=form)

@main.route('/transactions/edit/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.user_id != current_user.id:
        flash('Bu işlemi düzenleme yetkiniz yok.', 'danger')
        return redirect(url_for('main.list_transactions'))
    
    form = TransactionForm(obj=transaction)
    if form.validate_on_submit():
        transaction.type = form.type.data
        transaction.amount = form.amount.data
        transaction.category = form.category.data
        transaction.description = form.description.data
        transaction.date = form.date.data
        db.session.commit()
        flash('İşlem başarıyla güncellendi.', 'success')
        return redirect(url_for('main.list_transactions'))
    return render_template('transactions/edit.html', form=form, transaction=transaction)

@main.route('/transactions/delete/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.user_id != current_user.id:
        return jsonify({'success': False})
    
    try:
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False})

@main.route('/budgets')
@login_required
def list_budgets():
    budgets = Budget.query.filter_by(user_id=current_user.id)\
        .order_by(Budget.start_date.desc())\
        .all()
    return render_template('budgets/list.html', budgets=budgets)

@main.route('/budgets/add', methods=['GET', 'POST'])
@login_required
def add_budget():
    form = BudgetForm()
    if form.validate_on_submit():
        budget = Budget(
            category=form.category.data,
            amount=form.amount.data,
            period=form.period.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            user_id=current_user.id
        )
        db.session.add(budget)
        db.session.commit()
        flash('Bütçe başarıyla oluşturuldu.', 'success')
        return redirect(url_for('main.list_budgets'))
    return render_template('budgets/add.html', form=form)

@main.route('/budgets/edit/<int:budget_id>', methods=['GET', 'POST'])
@login_required
def edit_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    if budget.user_id != current_user.id:
        flash('Bu bütçeyi düzenleme yetkiniz yok.', 'danger')
        return redirect(url_for('main.list_budgets'))
    
    form = BudgetForm(obj=budget)
    if form.validate_on_submit():
        budget.category = form.category.data
        budget.amount = form.amount.data
        budget.period = form.period.data
        budget.start_date = form.start_date.data
        budget.end_date = form.end_date.data
        db.session.commit()
        flash('Bütçe başarıyla güncellendi.', 'success')
        return redirect(url_for('main.list_budgets'))
    return render_template('budgets/edit.html', form=form, budget=budget)

@main.route('/budgets/delete/<int:budget_id>', methods=['POST'])
@login_required
def delete_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    if budget.user_id != current_user.id:
        return jsonify({'success': False})
    
    try:
        db.session.delete(budget)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False})

@main.route('/goals')
@login_required
def list_goals():
    goals = Goal.query.filter_by(user_id=current_user.id)\
        .order_by(Goal.deadline.asc())\
        .all()
    return render_template('goals/list.html', goals=goals)

@main.route('/goals/add', methods=['GET', 'POST'])
@login_required
def add_goal():
    form = GoalForm()
    if form.validate_on_submit():
        goal = Goal(
            title=form.title.data,
            description=form.description.data,
            target_amount=form.target_amount.data,
            current_amount=form.current_amount.data,
            deadline=form.deadline.data,
            status='active',
            user_id=current_user.id
        )
        db.session.add(goal)
        db.session.commit()
        flash('Hedef başarıyla oluşturuldu.', 'success')
        return redirect(url_for('main.list_goals'))
    return render_template('goals/add.html', form=form)

@main.route('/goals/edit/<int:goal_id>', methods=['GET', 'POST'])
@login_required
def edit_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id:
        flash('Bu hedefi düzenleme yetkiniz yok.', 'danger')
        return redirect(url_for('main.list_goals'))
    
    form = GoalForm(obj=goal)
    if form.validate_on_submit():
        goal.title = form.title.data
        goal.description = form.description.data
        goal.target_amount = form.target_amount.data
        goal.current_amount = form.current_amount.data
        goal.deadline = form.deadline.data
        db.session.commit()
        flash('Hedef başarıyla güncellendi.', 'success')
        return redirect(url_for('main.list_goals'))
    return render_template('goals/edit.html', form=form, goal=goal)

@main.route('/goals/delete/<int:goal_id>', methods=['POST'])
@login_required
def delete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id:
        return jsonify({'success': False})
    
    try:
        db.session.delete(goal)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False})

@main.route('/goals/update_progress/<int:goal_id>', methods=['POST'])
@login_required
def update_progress(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id:
        return jsonify({'success': False})
    
    try:
        current_amount = request.json.get('current_amount')
        if current_amount is not None:
            goal.current_amount = float(current_amount)
            if goal.current_amount >= goal.target_amount:
                goal.status = 'completed'
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False})

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@main.route('/settings')
@login_required
def settings():
    return render_template('settings.html') 