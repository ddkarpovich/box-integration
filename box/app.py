import click
from flask import Flask

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config.from_object('box.config.Config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)

csrf = CSRFProtect()
csrf.init_app(app)


from box.users import views, models as user_models
from box.integration import views, models


@app.cli.command("create-user")
@click.argument("username")
@click.argument("email")
@click.argument("password")
def create_user(username, email, password):
    new_user = user_models.User(
        email=email,
        username=username,
        is_active=True,
        is_admin=True,
        password_hash=generate_password_hash(password, method='sha256')
    )
    db.session.add(new_user)
    db.session.commit()
    print('New user created')
