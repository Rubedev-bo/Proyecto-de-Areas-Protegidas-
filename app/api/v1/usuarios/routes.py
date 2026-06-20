from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from marshmallow import ValidationError

from app.repositories.usuario_repository import usuario_repo
from app.schemas.usuario_schema import usuario_schema, usuarios_schema, usuario_update_schema

usuarios_bp = Blueprint("usuarios", __name__)


def _requiere_admin():
    """Helper: retorna 403 si el usuario no es admin."""
    claims = get_jwt()
    if claims.get("rol") != "admin":
        return jsonify({"error": "Acceso solo para administradores."}), 403
    return None


@usuarios_bp.get("/")
@jwt_required()
def listar_usuarios():
    error = _requiere_admin()
    if error:
        return error

    usuarios = usuario_repo.get_all()
    return jsonify({"usuarios": usuarios_schema.dump(usuarios)}), 200


@usuarios_bp.get("/<int:usuario_id>")
@jwt_required()
def obtener_usuario(usuario_id: int):
    error = _requiere_admin()
    if error:
        return error

    usuario = usuario_repo.get_by_id(usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado."}), 404

    return jsonify(usuario_schema.dump(usuario)), 200


@usuarios_bp.patch("/<int:usuario_id>")
@jwt_required()
def actualizar_usuario(usuario_id: int):
    error = _requiere_admin()
    if error:
        return error

    usuario = usuario_repo.get_by_id(usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado."}), 404

    datos = request.get_json(silent=True) or {}
    try:
        datos_limpios = usuario_update_schema.load(datos, partial=True)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 422

    usuario_repo.update(usuario, **datos_limpios)
    return jsonify(usuario_schema.dump(usuario)), 200


@usuarios_bp.delete("/<int:usuario_id>")
@jwt_required()
def desactivar_usuario(usuario_id: int):
    """Desactivación lógica (no elimina el registro)."""
    error = _requiere_admin()
    if error:
        return error

    usuario = usuario_repo.get_by_id(usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado."}), 404

    usuario_repo.update(usuario, activo=False)
    return jsonify({"mensaje": f"Usuario {usuario_id} desactivado."}), 200