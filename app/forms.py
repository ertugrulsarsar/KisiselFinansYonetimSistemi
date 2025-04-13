from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FloatField, TextAreaField, DateField, DecimalField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, NumberRange, Optional
from app.models import User, Category

class LoginForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    remember_me = BooleanField('Beni Hatırla')
    submit = SubmitField('Giriş Yap')

class RegistrationForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Şifreyi Tekrarla', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Kayıt Ol')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Bu kullanıcı adı zaten kullanılıyor.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Bu e-posta adresi zaten kullanılıyor.')

class TransactionForm(FlaskForm):
    amount = DecimalField('Tutar', validators=[DataRequired(), NumberRange(min=0.01)])
    description = StringField('Açıklama', validators=[DataRequired(), Length(max=200)])
    category_id = SelectField('Kategori', coerce=int, validators=[DataRequired()])
    type = SelectField('Tür', choices=[('income', 'Gelir'), ('expense', 'Gider')], validators=[DataRequired()])
    date = DateField('Tarih', validators=[DataRequired()])
    submit = SubmitField('Kaydet')

    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        self.category_id.choices = []

    def update_categories(self, transaction_type):
        categories = Category.query.filter_by(type=transaction_type).all()
        self.category_id.choices = [(c.id, c.name) for c in categories]

class BudgetForm(FlaskForm):
    amount = DecimalField('Bütçe Tutarı', validators=[DataRequired(), NumberRange(min=0.01)])
    category_id = SelectField('Kategori', coerce=int, validators=[DataRequired()])
    start_date = DateField('Başlangıç Tarihi', validators=[DataRequired()])
    end_date = DateField('Bitiş Tarihi', validators=[DataRequired()])
    submit = SubmitField('Kaydet')

    def __init__(self, *args, **kwargs):
        super(BudgetForm, self).__init__(*args, **kwargs)
        categories = Category.query.filter_by(type='expense').all()
        self.category_id.choices = [(c.id, c.name) for c in categories]

class GoalForm(FlaskForm):
    title = StringField('Hedef Adı', validators=[DataRequired(), Length(max=100)])
    target_amount = DecimalField('Hedef Tutar', validators=[DataRequired(), NumberRange(min=0.01)])
    current_amount = DecimalField('Mevcut Tutar', validators=[DataRequired(), NumberRange(min=0)])
    deadline = DateField('Son Tarih', validators=[DataRequired()])
    submit = SubmitField('Kaydet')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Mevcut Şifre', validators=[DataRequired()])
    new_password = PasswordField('Yeni Şifre', validators=[
        DataRequired(),
        Length(min=8, message='Şifre en az 8 karakter olmalıdır'),
        EqualTo('confirm_password', message='Şifreler eşleşmiyor')
    ])
    confirm_password = PasswordField('Yeni Şifre (Tekrar)', validators=[DataRequired()])
    submit = SubmitField('Şifreyi Güncelle') 