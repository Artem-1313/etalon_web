from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_script import Manager


app = Flask(__name__)

app.config['SECRET_KEY'] = 'dfdfsdfsdfdsfdsf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///etalon.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_object(__name__)
login_manager = LoginManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)

from project.models import Admin, Article

from project.views import main

app.register_blueprint(main)

from project.admin.admin import admin

app.register_blueprint(admin, url_prefix="/admin")


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(user_id)


if __name__ == "project":
    app.run(debug=True)
