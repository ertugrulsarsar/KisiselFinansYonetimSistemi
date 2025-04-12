from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.models import Transaction
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from app import db
import pandas as pd
import plotly.express as px
import plotly.utils
import json

reports = Blueprint('reports', __name__)

def get_all_categories():
    """Tüm kategorileri getir."""
    return db.session.query(Transaction.category).distinct().all()

def get_top_categories(start_date, end_date, limit=5):
    """En çok harcama yapılan kategorileri getir."""
    return db.session.query(
        Transaction.category.label('name'),
        func.sum(Transaction.amount).label('amount')
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'expense',
        Transaction.date.between(start_date, end_date)
    ).group_by(Transaction.category)\
    .order_by(func.sum(Transaction.amount).desc())\
    .limit(limit).all()

@reports.route('/dashboard')
@login_required
def dashboard():
    """Dashboard görünümünü oluştur."""
    # Son 12 ayın verilerini al
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # Toplam gelir ve gider
    total_income = db.session.query(
        func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'income',
        Transaction.date.between(start_date, end_date)
    ).scalar() or 0

    total_expense = db.session.query(
        func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'expense',
        Transaction.date.between(start_date, end_date)
    ).scalar() or 0
    
    # Aylık gelir-gider özeti
    monthly_summary = db.session.query(
        extract('year', Transaction.date).label('year'),
        extract('month', Transaction.date).label('month'),
        Transaction.type,
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.date.between(start_date, end_date)
    ).group_by(
        extract('year', Transaction.date),
        extract('month', Transaction.date),
        Transaction.type
    ).all()
    
    # Kategori bazlı harcama dağılımı
    category_summary = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'expense',
        Transaction.date.between(start_date, end_date)
    ).group_by(Transaction.category).all()
    
    # Grafik verilerini hazırla
    monthly_chart = None
    category_chart = None

    if monthly_summary:
        df_monthly = pd.DataFrame([{
            'Yıl': int(item.year),
            'Ay': int(item.month),
            'Tür': 'Gelir' if item.type == 'income' else 'Gider',
            'Toplam': float(item.total)
        } for item in monthly_summary])
        
        df_monthly = df_monthly.sort_values(by=['Yıl', 'Ay'])
        
        fig_monthly = px.line(df_monthly, 
                            x=['Yıl', 'Ay'], 
                            y='Toplam', 
                            color='Tür',
                            title='Aylık Gelir-Gider Grafiği',
                            labels={'Toplam': 'Tutar (₺)'})
        
        monthly_chart = {
            'data': fig_monthly.data,
            'layout': fig_monthly.layout
        }
        monthly_chart = json.loads(json.dumps(monthly_chart, cls=plotly.utils.PlotlyJSONEncoder))

    if category_summary:
        df_category = pd.DataFrame([{
            'Kategori': item.category,
            'Toplam': float(item.total)
        } for item in category_summary])
        
        fig_category = px.pie(df_category, 
                            values='Toplam', 
                            names='Kategori',
                            title='Kategori Bazlı Harcama Dağılımı')
        
        category_chart = {
            'data': fig_category.data,
            'layout': fig_category.layout
        }
        category_chart = json.loads(json.dumps(category_chart, cls=plotly.utils.PlotlyJSONEncoder))
    
    return render_template('reports/dashboard.html',
                         monthly_chart=monthly_chart,
                         category_chart=category_chart,
                         total_income=total_income,
                         total_expense=total_expense,
                         categories=get_all_categories(),
                         top_categories=get_top_categories(start_date, end_date))

@reports.route('/api/dashboard-data')
@login_required
def dashboard_data():
    """Dashboard verilerini API endpoint'i olarak döndür."""
    start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
    end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
    category = request.args.get('category', '')
    type_ = request.args.get('type', '')
    
    # Temel filtreler
    filters = [
        Transaction.user_id == current_user.id,
        Transaction.date.between(start_date, end_date)
    ]
    
    # Opsiyonel filtreler
    if category:
        filters.append(Transaction.category == category)
    if type_:
        filters.append(Transaction.type == type_)
    
    # Toplam gelir ve gider
    total_income = db.session.query(
        func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'income',
        Transaction.date.between(start_date, end_date)
    ).scalar() or 0

    total_expense = db.session.query(
        func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'expense',
        Transaction.date.between(start_date, end_date)
    ).scalar() or 0
    
    # Aylık özet
    monthly_summary = db.session.query(
        extract('year', Transaction.date).label('year'),
        extract('month', Transaction.date).label('month'),
        Transaction.type,
        func.sum(Transaction.amount).label('total')
    ).filter(*filters).group_by(
        extract('year', Transaction.date),
        extract('month', Transaction.date),
        Transaction.type
    ).all()
    
    # Kategori özeti
    category_summary = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total')
    ).filter(*filters).group_by(Transaction.category).all()
    
    # Grafikleri hazırla
    monthly_chart = None
    category_chart = None

    if monthly_summary:
        df_monthly = pd.DataFrame([{
            'Yıl': int(item.year),
            'Ay': int(item.month),
            'Tür': 'Gelir' if item.type == 'income' else 'Gider',
            'Toplam': float(item.total)
        } for item in monthly_summary])
        
        df_monthly = df_monthly.sort_values(by=['Yıl', 'Ay'])
        
        fig_monthly = px.line(df_monthly, 
                            x=['Yıl', 'Ay'], 
                            y='Toplam', 
                            color='Tür',
                            title='Aylık Gelir-Gider Grafiği',
                            labels={'Toplam': 'Tutar (₺)'})
        
        monthly_chart = {
            'data': fig_monthly.data,
            'layout': fig_monthly.layout
        }
        monthly_chart = json.loads(json.dumps(monthly_chart, cls=plotly.utils.PlotlyJSONEncoder))

    if category_summary:
        df_category = pd.DataFrame([{
            'Kategori': item.category,
            'Toplam': float(item.total)
        } for item in category_summary])
        
        fig_category = px.pie(df_category, 
                            values='Toplam', 
                            names='Kategori',
                            title='Kategori Bazlı Harcama Dağılımı')
        
        category_chart = {
            'data': fig_category.data,
            'layout': fig_category.layout
        }
        category_chart = json.loads(json.dumps(category_chart, cls=plotly.utils.PlotlyJSONEncoder))
    
    # En çok harcama yapılan kategoriler
    top_categories = [{
        'name': category.name,
        'amount': float(category.amount)
    } for category in get_top_categories(start_date, end_date)]
    
    return jsonify({
        'monthlyChart': monthly_chart,
        'categoryChart': category_chart,
        'summary': {
            'totalIncome': float(total_income),
            'totalExpense': float(total_expense)
        },
        'topCategories': top_categories
    })

@reports.route('/api/monthly-summary')
@login_required
def monthly_summary_api():
    """Aylık özet verilerini JSON formatında döndür."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    summary = db.session.query(
        extract('year', Transaction.date).label('year'),
        extract('month', Transaction.date).label('month'),
        Transaction.type,
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.date.between(start_date, end_date)
    ).group_by(
        extract('year', Transaction.date),
        extract('month', Transaction.date),
        Transaction.type
    ).all()
    
    result = [{
        'year': int(item.year),
        'month': int(item.month),
        'type': item.type,
        'total': float(item.total)
    } for item in summary]
    
    return jsonify(result) 