from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect
from flask_cors import CORS
from marshmallow import Schema


db = SQLAlchemy()
migrate = Migrate()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Por favor debe iniciar sesión para continuar"
login_manager.login_message_category = "warning"


jwt = JWTManager()
bcrypt = Bcrypt()

csrf = CSRFProtect()


cors = CORS()

Column = db.Column