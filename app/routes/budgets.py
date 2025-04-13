from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import Budget, Transaction
from app import db
from datetime import datetime

bp = Blueprint('budgets', __name__)

@bp.route('/budgets')
@login_required
def list_budgets():
    budgets = Budget.query.filter_by(user_id=current_user.id).all()
    return render_template('budgets/list.html', budgets=budgets)

@bp.route('/budgets/add', methods=['GET', 'POST'])
@login_required
def add_budget():
    if request.method == 'POST':
        category = request.form.get('category')
        amount = float(request.form.get('amount'))
        period = request.form.get('period')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')

        budget = Budget(
            user_id=current_user.id,
            category=category,
            amount=amount,
            period=period,
            start_date=start_date,
            end_date=end_date
        )
        db.session.add(budget)
        db.session.commit()
        flash('Bütçe başarıyla oluşturuldu.', 'success')
        return redirect(url_for('budgets.list_budgets'))

    return render_template('budgets/add.html')

@bp.route('/budgets/<int:id>/delete', methods=['POST'])
@login_required
def delete_budget(id):
    budget = Budget.query.get_or_404(id)
    if budget.user_id != current_user.id:
        return jsonify({'success': False})
    
    try:
        db.session.delete(budget)
        db.session.commit()
        return jsonify({'success': True})
    except:
        db.session.rollback()
        return jsonify({'success': False}) 