from flask_login import UserMixin
from . import db, app


class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(5), unique=True)
    psw = db.Column(db.String(500), nullable=True)
    article = db.relationship('Article', backref='admin_author', lazy='dynamic')
    description = db.Column(db.String(500), nullable=True)
    avatar = db.Column(db.String(), default="default1314.jpg")

    def get_login(self):
        return self.login

    def __repr__(self):
        return f"{self.login}"


#создаем таблицу многое-ко-многим для постов и тэгов
articles_tags = db.Table('articles_tags',
                      db.Column('article_id', db.Integer, db.ForeignKey('article.id')),
                        db.Column('tag_id',db.Integer, db.ForeignKey('tag.id'))
)

class Article(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(), nullable=True)
    title = db.Column(db.String(), nullable=True)
    text = db.Column(db.String(), nullable=True)
    url = db.Column(db.String(), default="static/images/title_img/3czIqwedc11!!asdaqq.jpg")
    date_post = db.Column(db.DateTime)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)

    tags = db.relationship('Tag', secondary=articles_tags, backref=db.backref('articles', lazy='dynamic'))

    def __repr__(self):
        return f"{self.title}"


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=True)

    def __repr__(self):
        return f"{self.name}"


class Documents(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(), nullable=True)
    name = db.Column(db.String(), nullable=True)
    description = db.Column(db.String(), nullable=True)
    path = db.Column(db.String(), nullable=True)


class Telephones(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit = db.Column(db.String(), nullable=True)
    calling_name = db.Column(db.String(), nullable=True)
    abonent = db.Column(db.String(), nullable=True)
    ats = db.Column(db.String(), nullable=True)
    mosi = db.Column(db.String())
    zsoi = db.Column(db.String())


class Emails(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit = db.Column(db.String(), nullable=True)
    calling_name = db.Column(db.String(), nullable=True)
    asu_e = db.Column(db.String(), nullable=True)


class Commanders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.String(), nullable=True)
    position = db.Column(db.String(), nullable=True)
    full_name = db.Column(db.String(), nullable=True)
    img = db.Column(db.String(), default="static/images/title_img/3czIqwedc11!!asdaqq.jpg")
    state = db.Column(db.String(), nullable=True)
