from flask import Flask
from datetime import datetime

def register_filters(app: Flask):
    @app.template_filter('currency')
    def currency_filter(value):
        """Para birimini formatlar"""
        if value is None:
            return "0.00 ₺"
        return f"{value:,.2f} ₺"

    @app.template_filter('date')
    def date_filter(value):
        """Tarihi formatlar"""
        if value is None:
            return ""
        if isinstance(value, str):
            value = datetime.strptime(value, '%Y-%m-%d')
        return value.strftime('%d.%m.%Y')

    @app.template_filter('datetime')
    def datetime_filter(value):
        """Tarih ve saati formatlar"""
        if value is None:
            return ""
        if isinstance(value, str):
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return value.strftime('%d.%m.%Y %H:%M')

    @app.template_filter('percentage')
    def percentage_filter(value):
        """Yüzde değerini formatlar"""
        if value is None:
            return "0%"
        return f"{value:.1f}%" 