import os, shutil, zipfile

from os.path import basename
from flask import Blueprint, render_template, request, redirect, url_for, \
    flash, session, send_from_directory, jsonify, abort
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from project.admin.resize_img import resize_img, rename_file, allowed_files
from project.admin.delete_needless_images import del_img
from project.admin.zip_doc import zip_doc
from project.models import *
from datetime import datetime
from project import db, app
from project.admin.forms import *
from sqlalchemy import func, desc
from PIL import Image
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

admin = Blueprint('admin', __name__, template_folder="templates", static_folder="static")

menu_admin = [{"name": "Статті", "url": "/admin/"}, {"name": "Додати статтю", "url": "/admin/add_post"},
              {"name": "Вийти", "url": "/admin/logout"}, {"name": "Додати документ", "url": "/admin/add_doc"}]


def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.login == "artem":
            return f(*args, **kwargs)
        else:
            flash("Тільки суперадміни можуть відвідати цю сторінку", category="success")
            return redirect(url_for('admin.show_posts'))

    return wrap


@admin.app_errorhandler(401)
def unauthorized(error):
    return render_template("admin/unauth.html"), 401


@admin.app_errorhandler(404)
def page_not_found(error):
    return render_template("admin/page_not_found.html"), 404


@admin.route("/", methods=["POST", "GET"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for("admin.show_posts"))
    login_admin = LoginAdmin()
    if login_admin.validate_on_submit():
        user = Admin.query.filter(Admin.login == login_admin.login.data).first()
        if user and check_password_hash(user.psw, login_admin.psw.data):
            rm = login_admin.remainme.data
            login_user(user, remember=rm)
            return redirect(request.args.get("next") or url_for("admin.show_posts"))
        else:
            flash("Невірний логін або пароль!")

    return render_template("admin/index.html", form_admin=login_admin)


@admin.route("/show_docs/<type_of_doc>", methods=["POST", "GET"])
@login_required
def show_docs(type_of_doc):
    docs = Documents.query.filter_by(type=type_of_doc).all()
    if type_of_doc not in ['asu_doc', 'isd_doc', 'cyber_doc']:
        abort(404)
    return render_template("admin/show_docs.html", docs=docs, menu=menu_admin)


@admin.route("/add_doc", methods=["POST", "GET"])
@login_required
def add_doc():
    form = AddDocumentsForm()
    if form.validate_on_submit():
        file = form.path.data

        file_name = secure_filename(rename_file(file.filename))
        docs = Documents(type=form.type.data, name=form.name.data, description=form.description.data,
                         path=file_name)
        db.session.add(docs)
        db.session.commit()
        file.save(os.path.join("static", "docs", file_name))
        zip_ = zip_doc(file_name)

        try:
            with zipfile.ZipFile(os.path.join("static", "docs", zip_.rename_to_zip()), 'w') as myzip:
                myzip.write(os.path.join("static", "docs", file_name),
                            basename(os.path.join("static", "docs", file_name)))
        except OSError as e:
            print(e)

        return redirect(url_for("admin.show_docs", type_of_doc=form.type.data))

    return render_template("admin/add_doc_form.html", form=form, menu=menu_admin)


@admin.route("/add_post", methods=["POST", "GET"])
@login_required
def add_post():
    form = AddPostForm()
    if form.validate_on_submit():
        file = form.img_post.data
        # Если есть изображение для заголовка
        if file:
            new_filename = rename_file(file.filename)
            path = os.path.join("static", "images", "title_img", new_filename)
            file.save(path)
            img_check = resize_img(path, 210, 175)

            if not img_check.check_img_size():
                os.remove(path)
                flash("Розмір зображення менший ніж 210х175")
                return redirect(url_for("admin.add_post"))
            else:
                img_check.resize()
                article = Article(type=form.type.data, title=request.form['title'], text=request.form['post'],
                                  url=os.path.join(path), date_post=datetime.utcnow(),
                                  admin_id=current_user.get_id())

        # Добавления поста без изображения
        else:
            article = Article(type=form.type.data, title=request.form['title'], text=request.form['post'],
                              date_post=datetime.utcnow(),
                              admin_id=current_user.get_id())

        if form.tag.data:
            tag = form.tag.data
            tag_list = list(dict.fromkeys(tag.lower().split(",")))
            #ttt = [i.strip() for i in tag_list]
            for tag_ in tag_list:
                tag_exists = Tag.query.filter_by(name=tag_).first()
                if tag_exists:
                    article.tags.append(tag_exists)
                else:
                    new_tag = Tag(name=tag_)
                    db.session.add(new_tag)
                    article.tags.append(new_tag)

        db.session.add(article)
        db.session.commit()

        id_art = db.session.query(func.max(Article.id)).scalar()
        if id_art is None:
            id_art = 0
        del_similar_img = del_img(request.form['post'], str(id_art))
        del_similar_img.del_i()

        flash("Стаття успішно додана", category="success")
        return redirect(url_for("admin.show_posts"))

    return render_template("admin/add_posts_form.html", form=form, menu=menu_admin)


@admin.route("/posts")
@login_required
def show_posts():
    page = request.args.get('page', 1, type=int)
    # posts = Article.query.order_by(desc(Article.date_post)).paginate(page=page, per_page=10)
    posts = Article.query.order_by(desc(Article.date_post)).filter_by(admin_id=current_user.get_id()).paginate(
        page=page, per_page=10)
    return render_template("admin/posts.html", posts=posts, menu=menu_admin)


@admin.route("/delete/<id>")
@login_required
def delete_post(id):
    # удаляем изображение для поста
    post = Article.query.get_or_404(id)
    if post.admin_id != int(current_user.get_id()):
        flash(" Ви не можете видалити пост іншого адміністратора!", category="danger")
        return redirect(url_for("admin.show_posts"))
    if post.url != 'static/images/title_img/3czIqwedc11!!asdaqq.jpg':
        os.remove(post.url)
    if post.tags:
        # сохраняю тэги поста во временный массив
        tmp_list = post.tags
        # удаляю тэги связанные с постом
        post.tags = []
        db.session.commit()
        # проверяю во временном массиве у удаленного поста тэги, если эти тэги несвязаны с постами - их удаляем
        for t_ in tmp_list:
            print(t_.name)
            t_exists = Tag.query.filter_by(name=t_.name).first()
            if t_exists.articles.count() == 0:
                db.session.delete(t_exists)
                db.session.commit()

    db.session.delete(post)
    db.session.commit()

    # удаляем папку с изображениями для поста
    path = os.path.join(os.getcwd(), 'static', 'images')
    shutil.rmtree(os.path.join('static', 'images', str(id)), ignore_errors=True)
    flash(" Пост успішно видалено", category="success")
    return redirect(url_for('admin.show_posts'))


@admin.route("/edit_doc/<int:id>", methods=['post', 'get'])
@login_required
def edit_doc(id):
    form = EditDocumentsForm()
    docs = Documents.query.get_or_404(id)
    if form.validate_on_submit():
        file = form.path.data
        if file:
            path_to_pdf = os.path.join("static", "docs", docs.path)
            rename_pdf = zip_doc(docs.path)
            path_to_zip = os.path.join("static", "docs", rename_pdf.rename_to_zip())
            if os.path.isfile(path_to_pdf):
                os.remove(path_to_pdf)
                os.remove(path_to_zip)
            file_name = secure_filename(rename_file(file.filename))
            docs.path = file_name
            file.save(os.path.join("static", "docs", file_name))
            zip_ = zip_doc(file_name)

            try:
                with zipfile.ZipFile(os.path.join("static", "docs", zip_.rename_to_zip()), 'w') as myzip:
                    myzip.write(os.path.join("static", "docs", file_name),
                                basename(os.path.join("static", "docs", file_name)))
            except OSError as e:
                print(e)

        docs.name = form.name.data
        docs.description = form.description.data
        db.session.commit()
        flash("Документ змінено")
        return redirect(url_for("admin.show_docs", type_of_doc=docs.type))

    return render_template("admin/edit_doc.html", form=form, docs=docs)


@admin.route("/delete_doc/<int:id>", methods=['post', 'get'])
@login_required
def delete_doc(id):
    del_doc = Documents.query.get_or_404(id)
    path_to_pdf = os.path.join("static", "docs", del_doc.path)
    rename_pdf = zip_doc(del_doc.path)
    path_to_zip = os.path.join("static", "docs", rename_pdf.rename_to_zip())
    if os.path.isfile(path_to_pdf):
        os.remove(path_to_pdf)
        os.remove(path_to_zip)

    db.session.delete(del_doc)
    db.session.commit()

    return redirect(url_for('admin.show_docs', type_of_doc=del_doc.type))


@admin.route("/edit/<int:id>", methods=['post', 'get'])
@login_required
def edit(id):
    form = EditPostForm()
    ed_post = Article.query.get_or_404(id)
    if ed_post.admin_id != int(current_user.get_id()):
        flash(" Ви не можете редагувати статтю іншого адміністратора! ", category="danger")
        return redirect(url_for("admin.show_posts"))
    if form.validate_on_submit():
        file = form.img_post.data
        if file:
            # Сохраняем переименованное изображение в static\images\title_img
            new_filename = secure_filename(rename_file(file.filename))
            path = os.path.join('static', 'images', 'title_img', new_filename)
            file.save(path)
            # Проверяем размеры изображения
            image_check = resize_img(path, 210, 175)
            if not image_check.check_img_size():
                os.remove(path)
                flash("Розмір зображення менший ніж 210х175", category='danger')
                return redirect(url_for("admin.edit", id=ed_post.id))
            else:
                image_check.resize()
                if ed_post.url != 'static/images/title_img/3czIqwedc11!!asdaqq.jpg':
                    os.remove(ed_post.url)
                ed_post.type = form.type.data
                ed_post.title = form.title.data
                ed_post.text = form.post.data
                ed_post.url = os.path.join(path)
                # db.session.commit()
                # del_similar_img = del_img(form.post.data, ed_post.id)
                # del_similar_img.del_i()
                # flash("Статтю змінено!", category='success')
                # return redirect(url_for("admin.show_posts"))

        else:

            ed_post.type = form.type.data
            ed_post.title = form.title.data
            ed_post.text = form.post.data

        tag = form.tag.data
        print(tag)
        if not tag and ed_post.tags:
            tmp_ = ed_post.tags

            ed_post.tags = []
            for tag_ in tmp_:
                tag_exists = Tag.query.filter_by(name=tag_.name).first()
                if tag_exists:
                    db.session.delete(tag_exists)
                   # db.session.commit()
            db.session.commit()
        if tag:
            tmp_list = ed_post.tags
            ed_post.tags = []
            tag_list = list(dict.fromkeys(tag.lower().split(",")))
            for tag_ in tag_list:
                tag_exists = Tag.query.filter_by(name=tag_).first()
                if tag_exists:
                    print(tag_exists)
                    ed_post.tags.append(tag_exists)
                    db.session.commit()
                else:
                    print("i hete")
                    new_tag = Tag(name=tag_)
                    db.session.add(new_tag)
                    ed_post.tags.append(new_tag)
                    db.session.commit()

            tmp_list1 = ed_post.tags
            print(tmp_list1)
            for i in tmp_list:
                tag_exists = Tag.query.filter_by(name=i.name).first()
                if tag_exists.articles.count() == 0:
                   db.session.delete(tag_exists)
                   db.session.commit()


        db.session.commit()

        del_similar_img = del_img(form.post.data, ed_post.id)
        del_similar_img.del_i()

        flash("Статтю змінено!", category='success')
        return redirect(url_for("admin.show_posts"))

    return render_template("admin/edit.html", ed_post=ed_post.text, menu=menu_admin, form=form, title_data=ed_post,
                           id=id, tags=ed_post.tags)


@admin.route("/logout")
@login_required
def logout_admin():
    logout_user()
    return redirect(url_for("admin.index"))


@admin.route("/uploading", methods=['POST'])
@login_required
def uploading():
    file = request.files.get('file')
    if file:
        id_art = db.session.query(func.max(Article.id)).scalar()
        if id_art is None:
            id_art = 0
        filename = secure_filename(rename_file(file.filename))
        path = os.path.join(app.root_path, 'static', 'images', str(id_art + 1))
        if not os.path.exists(path):
            os.mkdir(path)
        file.save(os.path.join('static', 'images', str(id_art + 1), filename))
        return jsonify({'location': os.path.join('/static/images/', str(id_art + 1), filename).replace("\\", "/")})


@admin.route("/uploading_edit/<int:id>", methods=['POST', 'GET'])
@login_required
def uploading_edit(id):
    file = request.files.get('file')
    if file:
        print(id)
        filename = secure_filename(rename_file(file.filename))
        path = os.path.join(app.root_path, 'static', 'images', str(id))
        if not os.path.exists(path):
            os.mkdir(path)
        file.save(os.path.join('static', 'images', str(id), filename))
    return jsonify({'location': os.path.join('/static/images/', str(id), filename).replace("\\", "/")})


@admin.route("/add_phone", methods=["POST", "GET"])
@login_required
def add_phone():
    form = AddPhone()
    if form.validate_on_submit():
        try:
            phones = Telephones(unit=form.unit.data, calling_name=form.calling_name.data, abonent=form.abonent.data,
                                ats=form.ats.data, mosi=form.mosi.data, zsoi=form.zsoi.data)
            db.session.add(phones)
            db.session.commit()
            flash("Номер успішно доданий до довідника", category="success")
            return redirect(url_for("admin.show_phones"))
        except:
            db.session.rollback()
    return render_template("admin/add_phone.html", form=form)


@admin.route("/show_phones")
@login_required
def show_phones():
    phones = Telephones.query.all()
    return render_template("admin/show_phones.html", phones=phones)


@admin.route("/delete_phones/<int:id>", methods=['post', 'get'])
@login_required
def delete_phones(id):
    del_phone = Telephones.query.get_or_404(id)
    db.session.delete(del_phone)
    db.session.commit()
    return redirect(url_for('admin.show_phones'))


@admin.route("/edit_phones/<int:id>", methods=['post', 'get'])
@login_required
def edit_phones(id):
    form = AddPhone()
    edit_phones = Telephones.query.get_or_404(id)
    if form.validate_on_submit():
        edit_phones.unit = form.unit.data
        edit_phones.calling_name = form.calling_name.data
        edit_phones.abonent = form.abonent.data
        edit_phones.ats = form.ats.data
        edit_phones.mosi = form.mosi.data
        edit_phones.zsoi = form.zsoi.data
        db.session.commit()
        flash("Номер успішно змінено", category="success")
        return redirect(url_for("admin.show_phones"))

    return render_template("admin/edit_phones.html", form=form, phones=edit_phones)


@admin.route("/add_email", methods=['post', 'get'])
@login_required
def add_email():
    form = AddEmail()
    if form.validate_on_submit():
        try:
            email = Emails(unit=form.unit.data, calling_name=form.calling_name.data, asu_e=form.asu_e.data)
            db.session.add(email)
            db.session.commit()
            flash("Email успішно додано!", category="success")
            return redirect(url_for("admin.show_emails"))
        except:
            db.session.rollback()
    return render_template("admin/add_email.html", form=form)


@admin.route("/show_emails")
@login_required
def show_emails():
    emails = Emails.query.all()
    return render_template("admin/show_emails.html", emails=emails)


@admin.route("/edit_email/<int:id>", methods=['post', 'get'])
@login_required
def edit_email(id):
    form = AddEmail()
    edit_email = Emails.query.get_or_404(id)
    if form.validate_on_submit():
        edit_email.unit = form.unit.data
        edit_email.calling_name = form.calling_name.data
        edit_email.asu_e = form.asu_e.data
        db.session.commit()
        flash(" Email успішно змінено!", category="success")
        return redirect(url_for("admin.show_emails"))

    return render_template("admin/edit_emails.html", form=form, emails=edit_email)


@admin.route("/delete_email/<int:id>")
@login_required
def delete_email(id):
    del_email = Emails.query.get_or_404(id)
    db.session.delete(del_email)
    db.session.commit()
    return redirect(url_for('admin.show_emails'))


@admin.route("/add_commanders", methods=['post', 'get'])
@login_required
def add_commanders():
    form = AddCommander()
    if form.validate_on_submit():
        file = form.img.data
        new_filename = rename_file(file.filename)
        filename = secure_filename(new_filename)

        path = os.path.join("static", "images", "commanders", filename)
        file.save(path)
        img = Image.open(path)
        img = img.resize((682, 1024))
        img.save(path, quality=60, optimize=True)
        try:
            commander = Commanders(rank=form.rank.data, position=form.position.data, full_name=form.full_name.data,
                                   img=filename, state=form.state.data)
            db.session.add(commander)
            db.session.commit()

        except:
            db.session.rollback()

    return render_template("admin/add_commanders.html", form=form)


@admin.route("/show_commanders")
@login_required
def show_commanders():
    commanders = Commanders.query.all()
    return render_template("admin/show_commanders.html", commanders=commanders)


@admin.route("/edit_commanders/<int:id>", methods=['post', 'get'])
@login_required
def edit_commanders(id):
    form = EditCommander()
    commander = Commanders.query.get_or_404(id)
    if form.validate_on_submit():
        commander.rank = form.rank.data
        commander.position = form.position.data
        commander.full_name = form.full_name.data
        commander.state = form.state.data
        file = form.img.data
        if file:
            # Удаляем старую фотку командира
            if os.path.isfile(os.path.join("static", "images", "commanders", commander.img)):
                os.remove(os.path.join("static", "images", "commanders", commander.img))
            new_filename = rename_file(file.filename)
            filename = secure_filename(new_filename)
            path = os.path.join("static", "images", "commanders", filename)
            file.save(path)

            img = Image.open(path)
            img = img.resize((682, 1024))
            img.save(path, quality=60, optimize=True)
            commander.img = new_filename

        db.session.commit()
        return redirect(url_for("admin.show_commanders"))

    return render_template("admin/edit_commanders.html", form=form, commander=commander)


@admin.route("/delete_commanders/<int:id>", methods=['post', 'get'])
@login_required
def delete_commanders(id):
    del_commanders = Commanders.query.get_or_404(id)
    path_to_image = os.path.join("static", "images", "commanders", del_commanders.img)
    if os.path.isfile(path_to_image):
        os.remove(path_to_image)
    db.session.delete(del_commanders)
    db.session.commit()
    return redirect(url_for("admin.show_commanders"))


@admin.route("/change_password", methods=['post', 'get'])
@login_required
def change_password():
    form = ChangePsw()
    if form.validate_on_submit():
        user = Admin.query.filter_by(id=current_user.get_id()).first()

        if check_password_hash(user.psw, form.old_psw.data):
            user.psw = generate_password_hash(form.new_psw_repeat.data)
            db.session.commit()
            flash("Пароль успішно змінено!", category="success")
            return redirect(url_for("admin.change_password"))
        else:
            flash("Невірний старий пароль!", category="danger")
            return redirect(url_for("admin.change_password"))
            # raise ValidationError(f"Character  is not allowed in username.")

    return render_template("admin/change_password.html", form=form)


@admin.route("/add_admin", methods=['post', 'get'])
@login_required
@admin_required
def add_admin():
    form = AddAdmin()
    if form.validate_on_submit():
        if not Admin.query.filter_by(login=form.login.data).first():
            file = form.avatar.data
            if file:
                ava = rename_file(file.filename)
                path = os.path.join("static", "images", "ava", ava)
                file.save(path)
                img_check = resize_img(path, 125, 125)
                if not img_check.check_img_size():
                    os.remove(path)
                    flash("Розмір зображення менший ніж 125х125", category="error")
                    return redirect(url_for("admin.add_admin"))
                else:
                    img_check.resize()
                    user_admin = Admin(login=form.login.data, psw=generate_password_hash(form.new_psw_repeat.data),
                                       avatar=ava, description=form.description.data)

            else:
                user_admin = Admin(login=form.login.data, psw=generate_password_hash(form.new_psw_repeat.data),
                                   description=form.description.data)

            db.session.add(user_admin)
            db.session.commit()
            flash("Адміністратор успішно доданий!", category="success")
            return redirect(url_for("admin.add_admin"))
        else:
            flash("Адміністратор з таким логіном вже існує", category="danger")

    return render_template("admin/add_admin.html", form=form)


@admin.route("/change_ava", methods=['post', 'get'])
@login_required
def change_ava():
    form = ChangeAva()
    user = Admin.query.filter_by(id=current_user.get_id()).first()
    if form.validate_on_submit():

        file = form.avatar.data
        if file:
            # Удаляем старую фотку командира
            if os.path.isfile(
                    os.path.join("static", "images", "ava", user.avatar)) and user.avatar != "default1314.jpg":
                os.remove(os.path.join("static", "images", "ava", user.avatar))

            ava = rename_file(file.filename)
            path = os.path.join("static", "images", "ava", ava)
            file.save(path)
            img_check = resize_img(path, 125, 125)
            if not img_check.check_img_size():
                os.remove(path)
                flash("Розмір зображення менший ніж 125х125")
                return redirect(url_for("admin.change_ava", category="error"))
            else:
                img_check.resize()
                user.avatar = ava
                db.session.commit()
                flash("Аватарка успішно змінена!", category="success")
                return redirect(url_for("admin.change_ava"))

    return render_template("admin/change_ava.html", form=form, user=user)


@admin.route("show_admins")
@login_required
@admin_required
def show_admins():
    admin = Admin.query.all()
    return render_template("admin/show_admins.html", admins=admin)


@admin.route("/delete_admin/<int:id>", methods=['post', 'get'])
@login_required
@admin_required
def delete_admin(id):
    a1 = Admin.query.get_or_404(id)
    # запрет на удаление суперпользователя
    if a1.login == "artem":
        flash("Суперкористувача видалити неможливо", category="danger")
        return redirect(url_for("admin.show_admins"))
    # Удаление аватарка администратора
    if os.path.isfile(os.path.join("static", "images", "ava", a1.avatar)) and a1.avatar != "default1314.jpg":
        os.remove(os.path.join("static", "images", "ava", a1.avatar))
    # Проверка на наличие постов у админа и их удаление
    if a1.article.count() > 0:
        #
        for i in Article.query.filter_by(admin_id=id).all():
            # удаляем title img всех постов администратора
            if i.url != 'static/images/title_img/3czIqwedc11!!asdaqq.jpg':
                os.remove(i.url)
            # удаляем папку с изображениями постов
            if os.path.exists(os.path.join('static', 'images', str(i.id))):
                shutil.rmtree(os.path.join('static', 'images', str(i.id)), ignore_errors=True)

        # удаляем посты с БД
        Article.query.filter_by(admin_id=id).delete()

    # удаляем пользователя с бд
    db.session.delete(a1)
    db.session.commit()
    flash("Адміністратора успішно видалено", category="success")

    return redirect(url_for('admin.show_admins'))


@admin.route("/change_psw_by_admin/<int:id>", methods=['post', 'get'])
@login_required
@admin_required
def change_psw_by_admin(id):
    form = Change_psw_by_admin()
    user = Admin.query.get_or_404(id)
    if form.validate_on_submit():
        user.psw = generate_password_hash(form.new_psw_repeat.data)
        db.session.commit()
        flash("Пароль успішно змінено!", category="success")
        return redirect(url_for('admin.show_admins'))
    return render_template("admin/change_psw_by_admin.html", form=form)
