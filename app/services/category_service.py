from app.models import db, Category, Transaction
from sqlalchemy import func
from typing import List, Dict, Any, Tuple

class CategoryService:
    @staticmethod
    def get_all_categories() -> Tuple[List[Dict[str, Any]], str]:
        """Tüm kategorileri getirir"""
        try:
            categories = Category.query.all()
            return [category.to_dict() for category in categories], "Kategoriler başarıyla getirildi"
        except Exception as e:
            return [], f"Kategoriler getirilirken hata oluştu: {str(e)}"

    @staticmethod
    def create_category(data: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """Yeni kategori oluşturur"""
        try:
            # Veri doğrulama
            if not all(key in data for key in ['name', 'type']):
                return None, "Eksik bilgi"

            # Kategori adı kontrolü
            if Category.query.filter_by(name=data['name']).first():
                return None, "Bu kategori adı zaten kullanımda"

            # Kategori tipi kontrolü
            if data['type'] not in ['income', 'expense']:
                return None, "Geçersiz kategori tipi"

            category = Category(
                name=data['name'],
                description=data.get('description', ''),
                type=data['type'],
                color=data.get('color', '#000000'),
                icon=data.get('icon', 'default')
            )

            db.session.add(category)
            db.session.commit()

            return category.to_dict(), "Kategori başarıyla oluşturuldu"
        except Exception as e:
            db.session.rollback()
            return None, f"Kategori oluşturulurken hata oluştu: {str(e)}"

    @staticmethod
    def update_category(category_id: int, data: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """Kategori günceller"""
        try:
            category = Category.query.get(category_id)
            if not category:
                return None, "Kategori bulunamadı"

            # İsim değişikliği kontrolü
            if 'name' in data and data['name'] != category.name:
                if Category.query.filter_by(name=data['name']).first():
                    return None, "Bu kategori adı zaten kullanımda"
                category.name = data['name']

            # Tip değişikliği kontrolü
            if 'type' in data:
                if data['type'] not in ['income', 'expense']:
                    return None, "Geçersiz kategori tipi"
                category.type = data['type']

            # Diğer alanları güncelle
            if 'description' in data:
                category.description = data['description']
            if 'color' in data:
                category.color = data['color']
            if 'icon' in data:
                category.icon = data['icon']

            db.session.commit()
            return category.to_dict(), "Kategori başarıyla güncellendi"
        except Exception as e:
            db.session.rollback()
            return None, f"Kategori güncellenirken hata oluştu: {str(e)}"

    @staticmethod
    def delete_category(category_id: int) -> Tuple[bool, str]:
        """Kategori siler"""
        try:
            category = Category.query.get(category_id)
            if not category:
                return False, "Kategori bulunamadı"

            # Kategoriye ait işlem kontrolü
            if category.transactions:
                return False, "Bu kategoriye ait işlemler var. Önce işlemleri başka bir kategoriye taşıyın."

            db.session.delete(category)
            db.session.commit()
            return True, "Kategori başarıyla silindi"
        except Exception as e:
            db.session.rollback()
            return False, f"Kategori silinirken hata oluştu: {str(e)}"

    @staticmethod
    def get_category_statistics(category_id: int) -> Tuple[Dict[str, Any], str]:
        """Kategori istatistiklerini getirir"""
        try:
            category = Category.query.get(category_id)
            if not category:
                return None, "Kategori bulunamadı"

            # Toplam işlem tutarı
            total_amount = db.session.query(func.sum(Transaction.amount))\
                .filter_by(category_id=category_id)\
                .scalar() or 0

            # İşlem sayısı
            transaction_count = Transaction.query.filter_by(category_id=category_id).count()

            # Aylık ortalama
            monthly_avg = db.session.query(
                func.avg(func.sum(Transaction.amount))
            ).filter_by(category_id=category_id)\
             .group_by(func.extract('month', Transaction.transaction_date))\
             .scalar() or 0

            # Son 5 işlem
            recent_transactions = Transaction.query\
                .filter_by(category_id=category_id)\
                .order_by(Transaction.transaction_date.desc())\
                .limit(5)\
                .all()

            stats = {
                'category': category.to_dict(),
                'total_amount': float(total_amount),
                'transaction_count': transaction_count,
                'monthly_average': float(monthly_avg),
                'recent_transactions': [t.to_dict() for t in recent_transactions]
            }

            return stats, "Kategori istatistikleri başarıyla getirildi"
        except Exception as e:
            return None, f"Kategori istatistikleri getirilirken hata oluştu: {str(e)}"

    @staticmethod
    def transfer_transactions(from_category_id: int, to_category_id: int) -> Tuple[bool, str]:
        """Bir kategoriden diğerine işlemleri taşır"""
        try:
            from_category = Category.query.get(from_category_id)
            to_category = Category.query.get(to_category_id)

            if not from_category or not to_category:
                return False, "Kategori bulunamadı"

            if from_category.type != to_category.type:
                return False, "Kategoriler farklı tiplerde"

            # İşlemleri taşı
            Transaction.query\
                .filter_by(category_id=from_category_id)\
                .update({'category_id': to_category_id})

            db.session.commit()
            return True, "İşlemler başarıyla taşındı"
        except Exception as e:
            db.session.rollback()
            return False, f"İşlemler taşınırken hata oluştu: {str(e)}" 