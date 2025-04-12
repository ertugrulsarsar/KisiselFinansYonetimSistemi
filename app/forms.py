from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, NumberRange
from app.models import User

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