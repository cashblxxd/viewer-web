from flask_wtf.file import FileField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired


class AddNewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Описание', validators=[DataRequired()])
    file = FileField('Файл', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class ChangePasswordForm(FlaskForm):
    new_password = PasswordField('Новый пароль')  # , validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class ChangeApiKeyForm(FlaskForm):
    new_apikey = TextAreaField('Новый api ключ')  # , validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class ChangeClientIDForm(FlaskForm):
    new_clientid = TextAreaField('Новый Client ID')  # , validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class SignUpForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
