import click
from flask.cli import with_appcontext
from app import db
from app.models import Category

@click.command('init-categories')
@with_appcontext
def init_categories_command():
    """Temel kategorileri ekle."""
    categories = [
        # Gelir kategorileri
        {'name': 'Maaş', 'type': 'income'},
        {'name': 'Ek Gelir', 'type': 'income'},
        {'name': 'Yatırım Geliri', 'type': 'income'},
        {'name': 'Kira Geliri', 'type': 'income'},
        {'name': 'Diğer Gelirler', 'type': 'income'},
        
        # Gider kategorileri
        {'name': 'Kira', 'type': 'expense'},
        {'name': 'Faturalar', 'type': 'expense'},
        {'name': 'Market', 'type': 'expense'},
        {'name': 'Ulaşım', 'type': 'expense'},
        {'name': 'Sağlık', 'type': 'expense'},
        {'name': 'Eğitim', 'type': 'expense'},
        {'name': 'Eğlence', 'type': 'expense'},
        {'name': 'Giyim', 'type': 'expense'},
        {'name': 'Yemek', 'type': 'expense'},
        {'name': 'Diğer Giderler', 'type': 'expense'}
    ]
    
    for category_data in categories:
        category = Category.query.filter_by(name=category_data['name']).first()
        if not category:
            category = Category(**category_data)
            db.session.add(category)
    
    db.session.commit()
    click.echo('Temel kategoriler eklendi.') 