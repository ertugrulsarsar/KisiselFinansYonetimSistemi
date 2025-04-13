from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Transaction, Category
from app.forms import TransactionForm
from app import db
from datetime import datetime

bp = Blueprint('transactions', __name__)

@bp.route('/')
@login_required
def list_transactions():
    page = request.args.get('page', 1, type=int)
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.date.desc())\
        .paginate(page=page, per_page=10)
    return render_template('transactions/list.html', transactions=transactions)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    form = TransactionForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        transaction = Transaction(
            description=form.description.data,
            amount=form.amount.data,
            type=form.type.data,
            date=form.date.data,
            category_id=form.category_id.data,
            user_id=current_user.id
        )
        db.session.add(transaction)
        db.session.commit()
        flash('İşlem başarıyla eklendi.', 'success')
        return redirect(url_for('routes.transactions.list_transactions'))
    
    return render_template('transactions/add.html', form=form)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    if transaction.user_id != current_user.id:
        flash('Bu işlemi düzenleme yetkiniz yok.', 'danger')
        return redirect(url_for('routes.transactions.list_transactions'))
    
    form = TransactionForm(obj=transaction)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        transaction.description = form.description.data
        transaction.amount = form.amount.data
        transaction.type = form.type.data
        transaction.date = form.date.data
        transaction.category_id = form.category_id.data
        db.session.commit()
        flash('İşlem başarıyla güncellendi.', 'success')
        return redirect(url_for('routes.transactions.list_transactions'))
    
    return render_template('transactions/edit.html', form=form, transaction=transaction)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    if transaction.user_id != current_user.id:
        flash('Bu işlemi silme yetkiniz yok.', 'danger')
        return redirect(url_for('routes.transactions.list_transactions'))
    
    db.session.delete(transaction)
    db.session.commit()
    flash('İşlem başarıyla silindi.', 'success')
    return redirect(url_for('routes.transactions.list_transactions')) 