from flask import Blueprint, jsonify, current_app, render_template
from app.extensions import db

core_bp = Blueprint("core", __name__)


# ── Vistas del front (HTML) ──────────────────────────────────────────────────

@core_bp.get("/")
def index():
    """Mapa principal con las áreas protegidas."""
    return render_template("index.html")


@core_bp.get("/login")
def login_page():
    return render_template("login.html")


@core_bp.get("/registro")
def registro_page():
    return render_template("registro.html")


@core_bp.get("/avistamientos")
def avistamientos_page():
    return render_template("avistamientos.html")


@core_bp.get("/health")
def health_check():
    """Health-check que verifica la conexión a la base de datos."""
    try:
        db.session.execute(db.text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"

    return jsonify({
        "status": "ok" if db_status == "ok" else "degradado",
        "database": db_status,
        "env": current_app.config.get("ENV", "unknown"),
    }), 200 if db_status == "ok" else 503


@core_bp.get("/api/v1/")
def api_info():
    """Información de los endpoints disponibles."""
    return jsonify({
        "endpoints": {
            "auth": {
                "POST /api/v1/auth/register": "Registrar usuario",
                "POST /api/v1/auth/login": "Login → tokens JWT",
                "POST /api/v1/auth/refresh": "Renovar access_token",
                "GET  /api/v1/auth/me": "Perfil del usuario autenticado",
            },
            "areas_protegidas": {
                "GET /api/v1/areas-protegidas/": "Listar áreas protegidas",
                "GET /api/v1/areas-protegidas/<id>": "Detalle con GeoJSON",
                "GET /api/v1/areas-protegidas/punto?lat=&lon=": "Área por coordenada",
            },
            "biodiversidad": {
                "GET  /api/v1/biodiversidad/": "Listar avistamientos",
                "POST /api/v1/biodiversidad/": "Registrar avistamiento manual (JWT)",
                "POST /api/v1/biodiversidad/importar-gbif": "Importar desde GBIF (JWT)",
            },
            "usuarios": {
                "GET    /api/v1/usuarios/": "Listar usuarios (admin)",
                "GET    /api/v1/usuarios/<id>": "Detalle usuario (admin)",
                "PATCH  /api/v1/usuarios/<id>": "Actualizar usuario (admin)",
                "DELETE /api/v1/usuarios/<id>": "Desactivar usuario (admin)",
            },
        }
    }), 200