from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
)
from marshmallow import ValidationError

from app.services.auth_service import auth_service
from app.repositories.usuario_repository import usuario_repo
from app.schemas.usuario_schema import usuario_schema, login_schema

auth_bp = Blueprint("auth", __name__)


# ── POST /register ────────────────────────────────────────────────────────────

@auth_bp.post("/register")
def register():
    """
    Registra un nuevo usuario.

    Body:
        {
            "nombre": "Juan",
            "apellido": "Perez",
            "email": "juan@example.com",
            "password": "12345678",
            "password_confirm": "12345678",
            "rol": "visitante"   # opcional, default "visitante"
        }
    """
    datos = request.get_json(silent=True) or {}

    try:
        usuario_creado = auth_service.registrar_usuario(datos)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 422
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "mensaje": "Usuario registrado correctamente.",
        "usuario": usuario_creado,
    }), 201


# ── POST /login ────────────────────────────────────────────────────────────────

@auth_bp.post("/login")
def login():
    """
    Autentica al usuario y devuelve tokens JWT.

    Body:
        { "email": "juan@example.com", "password": "12345678" }
    """
    datos = request.get_json(silent=True) or {}

    try:
        datos_limpios = login_schema.load(datos)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 422

    try:
        resultado = auth_service.login_jwt(
            email=datos_limpios["email"],
            password=datos_limpios["password"],
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 401

    return jsonify(resultado), 200


# ── POST /refresh ────────────────────────────────────────────────────────────

@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    """Genera un nuevo access_token a partir de un refresh_token válido."""
    usuario_id = int(get_jwt_identity())

    try:
        resultado = auth_service.refresh_access_token(usuario_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 401

    return jsonify(resultado), 200


# ── GET /me ──────────────────────────────────────────────────────────────────

@auth_bp.get("/me")
@jwt_required()
def me():
    """Devuelve el perfil del usuario autenticado."""
    usuario_id = int(get_jwt_identity())
    usuario = usuario_repo.get_by_id(usuario_id)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado."}), 404

    return jsonify(usuario_schema.dump(usuario)), 200
