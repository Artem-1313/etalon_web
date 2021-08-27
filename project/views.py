from flask import Blueprint, render_template, abort, send_from_directory, request
from project.models import Article, Documents, Telephones, Emails, Commanders, Admin, Tag
from sqlalchemy import desc

import os

main = Blueprint('main', __name__)


@main.route("/")
def index():
    page = request.args.get('page', 1, type=int)
    posts = Article.query.order_by(desc(Article.date_post)).filter(Article.type == "news").paginate(page=page,
                                                                                                    per_page=5)
    posts_cyber = Article.query.order_by(desc(Article.date_post)).filter(Article.type == "cyber").limit(2).all()
    return render_template("main.html", posts=posts, posts_cyber=posts_cyber)


@main.route("/search", methods=['get'])
def search():
    page = request.args.get('page', 1, type=int)
    post = Article.query.filter(Article.title.contains(request.args.get('q', None))).paginate(page=page, per_page=3)
    return render_template("search.html", posts=post, q=request.args.get('q', None))


@main.route("/cyber")
def cyber():
    page = request.args.get('page', 1, type=int)
    posts = Article.query.order_by(desc(Article.date_post)).filter(Article.type == "cyber").paginate(page=page,
                                                                                                     per_page=5)
    return render_template("cyber.html", posts=posts)


@main.route("/communication")
def communication():
    page = request.args.get('page', 1, type=int)
    posts = Article.query.order_by(desc(Article.date_post)).filter(Article.type == "communication").paginate(page=page,
                                                                                                             per_page=5)

    return render_template("communication.html", posts=posts)


@main.route("/documents/<type_of_doc>")
def show_documents(type_of_doc):
    docs = Documents.query.filter(Documents.type == type_of_doc).all()

    return render_template("documents.html", documents=docs)


@main.route("/upload_doc/<path:doc>", methods=['GET', 'POST'])
def upload_doc(doc):
    return send_from_directory(directory=os.path.join("static", "docs"), filename=doc)


@main.route("/post/<int:id_article>")
def show_post(id_article):
    article = Article.query.filter(Article.id == id_article).first()
    if not article:
        abort(404)
    return render_template("article.html", article=article)


@main.route("/phonebook")
def phonebook():
    phone_numbers = Telephones.query.all()
    return render_template("phonebook.html", phones=phone_numbers)


@main.route("/emailbook")
def show_emails():
    emails = Emails.query.all()
    return render_template("emailbook.html", emails=emails)


@main.route("/commanders")
def show_commanders():
    commanders = Commanders.query.filter(Commanders.state == "Командування А1314").all()
    uzis_commanders = Commanders.query.filter(Commanders.state == "управління зв'язку").all()
    return render_template("commanders.html", commanders=commanders, uz_comm=uzis_commanders)


@main.route("/admin_articles/<user>", methods=['get', 'post'])
def admin_articles(user):
    page = request.args.get('page', 1, type=int)
    user_admin = Admin.query.filter_by(login=user).first()
    if user_admin is None:
        abort(404, description="asd")
    art = Article.query.filter_by(admin_id=user_admin.id).paginate(page=page, per_page=5)
    return render_template("admin_articles.html", posts=art, user=user_admin)


@main.route("/tag/<int:tag_id>", methods=['get', 'post'])
def show_tag(tag_id):
    page = request.args.get('page', 1, type=int)
    tag_post = Tag.query.get_or_404(tag_id)
    articles_tag = tag_post.articles.paginate(page=page, per_page=5)
    return render_template("tag.html", posts=articles_tag, tag_=tag_post)
