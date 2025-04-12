from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Transaction
from app.forms import TransactionForm
from datetime import datetime, timedelta

transactions = Blueprint('transactions', __name__)

@transactions.route('/list')
@login_required
def list_transactions():
    page = request.args.get('page', 1, type=int)
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.date.desc())\
        .paginate(page=page, per_page=10)
    return render_template('transactions/list.html', transactions=transactions)

@transactions.route('/add', methods=['GET', 'POST'])
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
        flash('İşlem başarıyla eklendi.', 'success')
        return redirect(url_for('main.index'))
    return render_template('transactions/add.html', form=form)

@transactions.route('/edit/<int:transaction_id>', methods=['GET', 'POST'])
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
        flash('İşlem başarıyla güncellendi.', 'success')
        return redirect(url_for('main.index'))
    
    form.type.data = transaction.type
    form.amount.data = transaction.amount
    form.category.data = transaction.category
    form.description.data = transaction.description
    
    return render_template('transactions/edit.html', form=form, transaction=transaction)

@transactions.route('/delete/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.user_id != current_user.id:
        flash('Bu işlemi silme yetkiniz yok.', 'danger')
        return redirect(url_for('main.index'))
    
    db.session.delete(transaction)
    db.session.commit()
    flash('İşlem başarıyla silindi.', 'success')
    return redirect(url_for('main.index'))

@transactions.route('/api/summary')
@login_required
def transaction_summary():
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= thirty_days_ago
    ).all()
    
    summary = {
        'total_income': sum(t.amount for t in transactions if t.type == 'income'),
        'total_expense': sum(t.amount for t in transactions if t.type == 'expense'),
        'transactions': [
            {
                'date': t.date.strftime('%Y-%m-%d'),
                'type': t.type,
                'category': t.category,
                'amount': t.amount
            } for t in transactions
        ]
    }
    return jsonify(summary) 