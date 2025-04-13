from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import Goal
from app import db
from datetime import datetime

bp = Blueprint('goals', __name__)

@bp.route('/goals')
@login_required
def list_goals():
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    return render_template('goals/list.html', goals=goals)

@bp.route('/goals/add', methods=['GET', 'POST'])
@login_required
def add_goal():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        target_amount = float(request.form.get('target_amount'))
        deadline = datetime.strptime(request.form.get('deadline'), '%Y-%m-%d')
        current_amount = float(request.form.get('current_amount', 0))

        goal = Goal(
            user_id=current_user.id,
            title=title,
            description=description,
            target_amount=target_amount,
            deadline=deadline,
            current_amount=current_amount
        )
        db.session.add(goal)
        db.session.commit()
        flash('Hedef başarıyla oluşturuldu.', 'success')
        return redirect(url_for('goals.list_goals'))

    return render_template('goals/add.html')

@bp.route('/goals/<int:id>/update', methods=['POST'])
@login_required
def update_goal(id):
    goal = Goal.query.get_or_404(id)
    if goal.user_id != current_user.id:
        return jsonify({'success': False})
    
    try:
        current_amount = float(request.form.get('current_amount'))
        goal.current_amount = current_amount
        goal.update_status()
        return jsonify({'success': True})
    except:
        db.session.rollback()
        return jsonify({'success': False})

@bp.route('/goals/<int:id>/delete', methods=['POST'])
@login_required
def delete_goal(id):
    goal = Goal.query.get_or_404(id)
    if goal.user_id != current_user.id:
        return jsonify({'success': False})
    
    try:
        db.session.delete(goal)
        db.session.commit()
        return jsonify({'success': True})
    except:
        db.session.rollback()
        return jsonify({'success': False}) 