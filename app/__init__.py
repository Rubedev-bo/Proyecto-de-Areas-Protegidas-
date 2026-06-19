from flask import Flask

from config import get_config
from app.extensions import db, migrate, login_manager, jwt, bcrypt, csrf, cors

def create_app(env_name: str | None = None) -> Flask:
    
    app = Flask(__name__, instance_relative_config=False)
    
    app.config.from_object(get_config(env_name))
    
    _init_extensions(app)
    
    _register_blueprints(app)
    
    _register_error_handlers(app)
    
    _register_shell_context(app)
    
    return app

def _init_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app,db)
    login_manager.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*":{"origins": app.config["CORS_ORIGINS"]}},
    )
    
    with app.app_context():
        from app.models import usuario, area_protegida, avistamiento
        

def _register_blueprints(app: Flask) -> None:
    from app.api.v1.auth.routes import auth_bp
    from app.api.v1.areas_protegidas.routes import areas_bp
    from app.api.v1.biodiversidad.routes import biodiversidad_bp
    from app.api.v1.usuarios.routes import usuarios_bp

    app.register_blueprint(auth_bp,         url_prefix="/api/v1/auth")
    app.register_blueprint(areas_bp,        url_prefix="/api/v1/areas-protegidas")
    app.register_blueprint(biodiversidad_bp, url_prefix="/api/v1/biodiversidad")
    app.register_blueprint(usuarios_bp,     url_prefix="/api/v1/usuarios")
    
    
    from app.core.routes import core_bp
    app.register_blueprint(core_bp)
    
    
    
def _register_error_handlers(app: Flask) -> None:
    """Manejadores centralizados de errores HTTP."""
    from flask import jsonify

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Solicitud inválida", "detalle": str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "No autenticado"}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Acceso prohibido"}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Recurso no encontrado"}), 404

    @app.errorhandler(422)
    def unprocessable(e):
        return jsonify({"error": "Datos no procesables", "detalle": str(e)}), 422

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return jsonify({"error": "Error interno del servidor"}), 500
    
    
def _register_shell_context(app: Flask) -> None:
    """Expone objetos útiles en `flask shell` sin importarlos manualmente."""

    @app.shell_context_processor
    def make_shell_context():
        from app.models.usuario import Usuario
        from app.models.area_protegida import AreaProtegida
        from app.models.avistamiento import Avistamiento
        return {
            "db": db,
            "Usuario": Usuario,
            "AreaProtegida": AreaProtegida,
            "Avistamiento": Avistamiento,
        }