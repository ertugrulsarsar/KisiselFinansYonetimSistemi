from app.models import db, Transaction, Category
from datetime import datetime, timedelta
from sqlalchemy import func
from typing import List, Dict, Any, Tuple

class TransactionService:
    @staticmethod
    def get_user_transactions(
        user_id: int,
        start_date: str = None,
        end_date: str = None,
        category_id: int = None,
        transaction_type: str = None
    ) -> Tuple[List[Dict[str, Any]], str]:
        """Kullanıcının işlemlerini filtrelerle getirir"""
        try:
            query = Transaction.query.filter_by(user_id=user_id)

            if start_date:
                query = query.filter(Transaction.transaction_date >= datetime.strptime(start_date, '%Y-%m-%d'))
            if end_date:
                query = query.filter(Transaction.transaction_date <= datetime.strptime(end_date, '%Y-%m-%d'))
            if category_id:
                query = query.filter_by(category_id=category_id)
            if transaction_type:
                query = query.filter_by(transaction_type=transaction_type)

            transactions = query.order_by(Transaction.transaction_date.desc()).all()
            return [t.to_dict() for t in transactions], "İşlemler başarıyla getirildi"
        except Exception as e:
            return [], f"İşlemler getirilirken hata oluştu: {str(e)}"

    @staticmethod
    def create_transaction(user_id: int, data: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """Yeni işlem oluşturur"""
        try:
            # Veri doğrulama
            required_fields = ['category_id', 'amount', 'transaction_type', 'transaction_date']
            if not all(field in data for field in required_fields):
                return None, "Eksik bilgi"

            # Kategori kontrolü
            category = Category.query.get(data['category_id'])
            if not category:
                return None, "Geçersiz kategori"

            # Tutar kontrolü
            try:
                amount = float(data['amount'])
                if amount <= 0:
                    return None, "Tutar 0'dan büyük olmalıdır"
            except ValueError:
                return None, "Geçersiz tutar"

            # İşlem tipi kontrolü
            if data['transaction_type'] not in ['income', 'expense']:
                return None, "Geçersiz işlem tipi"

            transaction = Transaction(
                user_id=user_id,
                category_id=data['category_id'],
                amount=amount,
                description=data.get('description', ''),
                transaction_type=data['transaction_type'],
                transaction_date=datetime.strptime(data['transaction_date'], '%Y-%m-%d')
            )

            db.session.add(transaction)
            db.session.commit()

            return transaction.to_dict(), "İşlem başarıyla oluşturuldu"
        except Exception as e:
            db.session.rollback()
            return None, f"İşlem oluşturulurken hata oluştu: {str(e)}"

    @staticmethod
    def update_transaction(user_id: int, transaction_id: int, data: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """İşlem günceller"""
        try:
            transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
            if not transaction:
                return None, "İşlem bulunamadı"

            if 'category_id' in data:
                category = Category.query.get(data['category_id'])
                if not category:
                    return None, "Geçersiz kategori"
                transaction.category_id = data['category_id']

            if 'amount' in data:
                try:
                    amount = float(data['amount'])
                    if amount <= 0:
                        return None, "Tutar 0'dan büyük olmalıdır"
                    transaction.amount = amount
                except ValueError:
                    return None, "Geçersiz tutar"

            if 'description' in data:
                transaction.description = data['description']

            if 'transaction_type' in data:
                if data['transaction_type'] not in ['income', 'expense']:
                    return None, "Geçersiz işlem tipi"
                transaction.transaction_type = data['transaction_type']

            if 'transaction_date' in data:
                transaction.transaction_date = datetime.strptime(data['transaction_date'], '%Y-%m-%d')

            db.session.commit()
            return transaction.to_dict(), "İşlem başarıyla güncellendi"
        except Exception as e:
            db.session.rollback()
            return None, f"İşlem güncellenirken hata oluştu: {str(e)}"

    @staticmethod
    def delete_transaction(user_id: int, transaction_id: int) -> Tuple[bool, str]:
        """İşlem siler"""
        try:
            transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
            if not transaction:
                return False, "İşlem bulunamadı"

            db.session.delete(transaction)
            db.session.commit()
            return True, "İşlem başarıyla silindi"
        except Exception as e:
            db.session.rollback()
            return False, f"İşlem silinirken hata oluştu: {str(e)}"

    @staticmethod
    def get_transaction_summary(user_id: int, start_date: str = None, end_date: str = None) -> Tuple[Dict[str, Any], str]:
        """İşlem özeti getirir"""
        try:
            query = Transaction.query.filter_by(user_id=user_id)

            if start_date:
                query = query.filter(Transaction.transaction_date >= datetime.strptime(start_date, '%Y-%m-%d'))
            if end_date:
                query = query.filter(Transaction.transaction_date <= datetime.strptime(end_date, '%Y-%m-%d'))

            # Toplam gelir ve gider
            income = db.session.query(func.sum(Transaction.amount))\
                .filter(Transaction.user_id == user_id, Transaction.transaction_type == 'income')\
                .scalar() or 0

            expense = db.session.query(func.sum(Transaction.amount))\
                .filter(Transaction.user_id == user_id, Transaction.transaction_type == 'expense')\
                .scalar() or 0

            # Kategori bazlı özet
            category_summary = db.session.query(
                Category.name,
                Category.type,
                func.sum(Transaction.amount).label('total')
            ).join(Transaction)\
             .filter(Transaction.user_id == user_id)\
             .group_by(Category.name, Category.type)\
             .all()

            # Son 30 günlük trend
            thirty_days_ago = datetime.now() - timedelta(days=30)
            daily_trend = db.session.query(
                Transaction.transaction_date,
                Transaction.transaction_type,
                func.sum(Transaction.amount).label('total')
            ).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= thirty_days_ago
            ).group_by(
                Transaction.transaction_date,
                Transaction.transaction_type
            ).all()

            summary = {
                'total_income': float(income),
                'total_expense': float(expense),
                'balance': float(income - expense),
                'category_summary': [{
                    'category': name,
                    'type': type_,
                    'total': float(total)
                } for name, type_, total in category_summary],
                'daily_trend': [{
                    'date': date.strftime('%Y-%m-%d'),
                    'type': type_,
                    'total': float(total)
                } for date, type_, total in daily_trend]
            }

            return summary, "Özet başarıyla getirildi"
        except Exception as e:
            return None, f"Özet getirilirken hata oluştu: {str(e)}" 