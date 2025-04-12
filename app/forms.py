from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, SelectField, TextAreaField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, NumberRange
from app.models import User, Budget
from datetime import datetime
from flask_login import current_user

class LoginForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    remember_me = BooleanField('Beni Hatırla')
    submit = SubmitField('Giriş Yap')

class RegistrationForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Şifre Tekrar', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Kayıt Ol')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Bu kullanıcı adı zaten kullanılıyor.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Bu email adresi zaten kullanılıyor.')

class TransactionForm(FlaskForm):
    type = SelectField('İşlem Türü', choices=[('income', 'Gelir'), ('expense', 'Gider')], validators=[DataRequired()])
    amount = FloatField('Miktar', validators=[DataRequired(), NumberRange(min=0.01)])
    category = StringField('Kategori', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Açıklama', validators=[Length(max=200)])
    submit = SubmitField('Kaydet')

class BudgetForm(FlaskForm):
    category = SelectField('Kategori', validators=[DataRequired()])
    amount = FloatField('Bütçe Miktarı', validators=[DataRequired(), NumberRange(min=0)])
    period = SelectField('Periyot', choices=[('monthly', 'Aylık'), ('yearly', 'Yıllık')], validators=[DataRequired()])
    start_date = DateField('Başlangıç Tarihi', validators=[DataRequired()])
    end_date = DateField('Bitiş Tarihi', validators=[DataRequired()])
    submit = SubmitField('Bütçe Oluştur')

    def __init__(self, *args, **kwargs):
        super(BudgetForm, self).__init__(*args, **kwargs)
        self.category.choices = [(cat, cat) for cat in current_user.categories]

    def validate(self):
        if not super(BudgetForm, self).validate():
            return False
        
        if self.start_date.data > self.end_date.data:
            self.end_date.errors.append('Bitiş tarihi başlangıç tarihinden önce olamaz.')
            return False
        
        # Aynı kategori ve tarih aralığında başka bir bütçe var mı kontrol et
        existing_budget = Budget.query.filter(
            Budget.user_id == current_user.id,
            Budget.category == self.category.data,
            Budget.start_date <= self.end_date.data,
            Budget.end_date >= self.start_date.data
        ).first()
        
        if existing_budget:
            self.category.errors.append('Bu kategori için belirtilen tarih aralığında zaten bir bütçe tanımlanmış.')
            return False
        
        return True

class GoalForm(FlaskForm):
    title = StringField('Hedef Başlığı', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Açıklama')
    target_amount = FloatField('Hedef Miktar', validators=[DataRequired(), NumberRange(min=0)])
    deadline = DateField('Son Tarih', validators=[DataRequired()])
    submit = SubmitField('Hedef Oluştur')

    def validate(self):
        if not super(GoalForm, self).validate():
            return False
        
        if self.deadline.data < datetime.utcnow().date():
            self.deadline.errors.append('Son tarih geçmiş bir tarih olamaz.')
            return False
        
        return True 