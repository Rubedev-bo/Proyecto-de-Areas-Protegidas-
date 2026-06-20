from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def roles_requeridos(*roles: str):
    """
    Decorador que verifica que el JWT del usuario tenga uno de los roles indicados.

    Uso:
        @areas_bp.delete("/<int:id>")
        @jwt_required()
        @roles_requeridos("admin")
        def eliminar_area(id):
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            rol_usuario = claims.get("rol", "visitante")
            if rol_usuario not in roles:
                return jsonify({
                    "error": f"Acceso denegado. Roles permitidos: {', '.join(roles)}"
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_requerido(fn):
    """Decorador de conveniencia para endpoints solo-admin."""
    return roles_requeridos("admin")(fn)


def investigador_requerido(fn):
    """Decorador para endpoints de investigadores y admins."""
    return roles_requeridos("admin", "investigador")(fn)
