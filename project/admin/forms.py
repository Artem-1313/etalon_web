from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, BooleanField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, regexp, EqualTo, ValidationError


class LoginAdmin(FlaskForm):
    login = StringField(render_kw={"placeholder": "Логін"}, validators=[DataRequired()])
    psw = PasswordField(render_kw={"placeholder": "Пароль"}, validators=[DataRequired()])
    remainme = BooleanField("Запам\'ятати мене", default=False)
    submit = SubmitField("Увійти")


class AddPostForm(FlaskForm):
    type = SelectField(u'Тип документи', choices=[('news', 'Новини'), ('cyber', 'Кібербезпека'),
                                                         ('communication', 'Зв\'язок ')], validators=[DataRequired()])
    title = StringField("Заголовок", validators=[DataRequired()])
    img_post = FileField('Зображення для посту', validators=[ FileAllowed(['jpeg', 'jpg', 'png'], message="Можливо завантажити файл лише у форматі JPG, JPEG, PNG ")])
    post = TextAreaField("Текст статті")
    tag = StringField("Тег")
    submit = SubmitField("Додати статтю")


class EditPostForm(FlaskForm):
    type = SelectField(u'Тип документи', choices=[('news', 'Новини'), ('cyber', 'Кібербезпека'),
                                                  ('communication', 'Зв\'язок ')], validators=[DataRequired()])
    title = StringField("Заголовок", validators=[DataRequired()])
    img_post = FileField('File', validators=[ FileAllowed(['jpeg', 'jpg', 'png'], message="Можливо завантажити файл лише у форматі JPG, JPEG, PNG ")])
    post = TextAreaField("Текст статті")
    tag = StringField("Тег")
    submit = SubmitField("Додати статтю")


class AddDocumentsForm(FlaskForm):
    type = SelectField(u'Programming Language', choices=[('asu_doc', 'АСУ "Дніпро"'), ('isd_doc', 'ІСД-Інтернет'), ('cyber_doc', 'Кібербезпека')],validators=[DataRequired()])
    name = StringField("Назва документу", validators=[DataRequired()])
    description = TextAreaField("Опис документу", validators=[DataRequired()])
    path = FileField('File', validators=[FileAllowed(['pdf'], message="Можливо завантажити файл лише у форматі pdf"), FileRequired()])
    submit = SubmitField("Додати документ")


class EditDocumentsForm(FlaskForm):
    name = StringField("Назва документу", validators=[DataRequired()])
    description = TextAreaField("Опис документу", validators=[DataRequired()])
    path = FileField('File', validators=[FileAllowed(['pdf'], message="Можливо завантажити файл лише у форматі pdf")])
    submit = SubmitField("Змінити документ")


class AddPhone(FlaskForm):
    unit = StringField("Військова частина", validators=[DataRequired()])
    calling_name = StringField("Позивний", validators=[DataRequired()])
    abonent = StringField("Абонент", validators=[DataRequired()])
    ats = StringField("АТС", validators=[DataRequired(), regexp('^[0-9]{5}$', message="Номер АТС має складатись лише з пяти цифр")])
    mosi = StringField("ЗСУ002", validators=[regexp('^[0-9]{0,5}$', message="Номер МОСІ має складатись лише з пяти цифр")])
    zsoi = StringField("ЗСУ001", validators=[regexp('^[0-9]{0,4}$', message="Номер ЗСОІ має складатись лише з чотирьох цифр")])
    submit = SubmitField("Додати")


class AddEmail(FlaskForm):
    unit = StringField("Військова частина", validators=[DataRequired()])
    calling_name = StringField("Позивний", validators=[DataRequired()])
    asu_e = StringField("АТС", validators=[DataRequired(), Email( message="Ви ввели невірну поштову адресу")])
    submit = SubmitField("Додати")


class AddCommander(FlaskForm):

    rank = SelectField(u'Rank',
                       choices=[('генерал-майор', 'генерал-майор'), ('бригадний генерал', 'бригадний генерал'), ('полковник', 'полковник'), ('підполковник', 'підполковник'), ('майор', 'майор')],
                       validators=[DataRequired()])
    position = StringField(validators=[DataRequired()])
    full_name = StringField(validators=[DataRequired()])
    img = FileField('File', validators=[FileRequired(), FileAllowed(['jpeg', 'jpg', 'png'], message="Можливо завантажити файл лише у форматі JPG, JPEG, PNG ")])
    state = SelectField(u'State',
                       choices=[('Командування А1314', 'Командування А1314'), ('управління зв\'язку', 'управління зв\'язку')],
                       validators=[DataRequired()])
    submit = SubmitField("Додати")


class EditCommander(FlaskForm):

    rank = SelectField(u'Rank',
                       choices=[('генерал-майор', 'генерал-майор'), ('бригадний генерал', 'бригадний генерал'), ('полковник', 'полковник'), ('підполковник', 'підполковник'), ('майор', 'майор')],
                       validators=[DataRequired()])
    position = StringField(validators=[DataRequired()])
    full_name = StringField(validators=[DataRequired()])
    img = FileField('File', validators=[FileAllowed(['jpeg', 'jpg', 'png'], message="Можливо завантажити файл лише у форматі JPG, JPEG, PNG ")])
    state = SelectField(u'State',
                       choices=[('Командування А1314', 'Командування А1314'), ('управління зв\'язку', 'управління зв\'язку')],
                       validators=[DataRequired()])
    submit = SubmitField("Змінити")


class ChangePsw(FlaskForm):
    old_psw = PasswordField(render_kw={"placeholder": "Старий пароль"}, validators=[DataRequired()])
    new_psw = PasswordField(render_kw={"placeholder": "Новий пароль"},
                            validators=[DataRequired(), EqualTo('new_psw_repeat', message="Паролі не співпадають")])
    new_psw_repeat = PasswordField(render_kw={"placeholder": "Підтвердіть новий пароль"},validators=[DataRequired()])
    submit = SubmitField("Змінити")


class AddAdmin(FlaskForm):
    login = StringField(render_kw={"placeholder": "Логін"}, validators=[DataRequired()])
    new_psw = PasswordField(render_kw={"placeholder": "Новий пароль"}, validators=[DataRequired(), EqualTo('new_psw_repeat', message="Паролі не співпадають")])
    new_psw_repeat = PasswordField(render_kw={"placeholder": "Підтвердіть новий пароль"}, validators=[DataRequired()])
    description = StringField(render_kw={"placeholder": "Відомості про адміністратора"}, validators=[DataRequired()])
    avatar = FileField('File', validators=[FileAllowed(['jpeg', 'jpg', 'png'], message="Можливо завантажити файл лише у форматі JPG, JPEG, PNG ")])
    submit = SubmitField("Додати")


class ChangeAva(FlaskForm):
    avatar = FileField('File', validators=[DataRequired(), FileAllowed(['jpeg', 'jpg', 'png'], message="Можливо завантажити файл лише у форматі JPG, JPEG, PNG ")])
    submit = SubmitField("Змінити")


class Change_psw_by_admin(FlaskForm):
    new_psw = PasswordField(render_kw={"placeholder": "Новий пароль"}, validators=[DataRequired(), EqualTo('new_psw_repeat', message="Паролі не співпадають")])
    new_psw_repeat = PasswordField(render_kw={"placeholder": "Підтвердіть новий пароль"}, validators=[DataRequired()])
    submit = SubmitField("Додати")