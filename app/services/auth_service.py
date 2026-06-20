from datetime import datetime, timezone
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_login import login_user, logout_user
from marshmallow import ValidationError

from app.models.usuario import Usuario
from app.repositories.usuario_repository import usuario_repo
from app.schemas.usuario_schema import usuario_create_schema, usuario_schema
from app.extensions import db


class AuthService:
    
    """Encapsula la lógica de autenticación y registro."""

    # ── Registro ──────────────────────────────────────────────────

    def registrar_usuario(self, datos: dict) -> dict:
        """
        Valida y crea un nuevo usuario.

        Args:
            datos: dict con nombre, apellido, email, password, password_confirm.

        Returns:
            dict con el usuario creado serializado.

        Raises:
            ValidationError: si los datos son inválidos.
        """
        # Validar con Marshmallow
        datos_limpios = usuario_create_schema.load(datos)

        # Crear usuario
        usuario = Usuario(
            nombre=datos_limpios["nombre"],
            apellido=datos_limpios["apellido"],
            email=datos_limpios["email"].lower().strip(),
            rol=datos_limpios.get("rol", "visitante"),
        )
        usuario.password = datos_limpios["password"]  # setter hashea la contraseña

        db.session.add(usuario)
        db.session.commit()

        return usuario_schema.dump(usuario)

    # ── Login JWT ─────────────────────────────────────────────────

    def login_jwt(self, email: str, password: str) -> dict:
        """
        Autentica al usuario y genera tokens JWT.

        Returns:
            dict con access_token, refresh_token y datos del usuario.

        Raises:
            ValueError: si las credenciales son inválidas.
        """
        usuario = usuario_repo.get_by_email(email)

        if not usuario or not usuario.verificar_password(password):
            raise ValueError("Correo o contraseña incorrectos.")

        if not usuario.activo:
            raise ValueError("La cuenta está desactivada.")

        # Actualizar último acceso
        usuario.ultimo_acceso = datetime.now(timezone.utc)
        db.session.commit()

        # Generar tokens
        access_token = create_access_token(
            identity=str(usuario.id),
            additional_claims={
                "email": usuario.email,
                "rol": usuario.rol,
            },
        )
        refresh_token = create_refresh_token(identity=str(usuario.id))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "usuario": usuario_schema.dump(usuario),
        }

    def refresh_access_token(self, usuario_id: int) -> dict:
        """Genera un nuevo access_token usando el refresh_token."""
        usuario = usuario_repo.get_by_id(usuario_id)
        if not usuario or not usuario.activo:
            raise ValueError("Usuario no válido.")

        nuevo_token = create_access_token(
            identity=str(usuario.id),
            additional_claims={"email": usuario.email, "rol": usuario.rol},
        )
        return {"access_token": nuevo_token}

    # ── Login con Flask-Login (sesión web) ────────────────────────

    def login_sesion(
        self, email: str, password: str, recordarme: bool = False
    ) -> Usuario:
        """
        Autentica y crea una sesión Flask-Login.
        Útil si además de la API tienes páginas web renderizadas.

        Returns:
            Usuario autenticado.
        """
        usuario = usuario_repo.get_by_email(email)

        if not usuario or not usuario.verificar_password(password):
            raise ValueError("Credenciales inválidas.")

        if not usuario.activo:
            raise ValueError("Cuenta desactivada.")

        login_user(usuario, remember=recordarme)

        usuario.ultimo_acceso = datetime.now(timezone.utc)
        db.session.commit()

        return usuario

    def logout_sesion(self) -> None:
        """Cierra la sesión Flask-Login."""
        logout_user()


# ── Instancia singleton ───────────────────────────────────────────────────────
auth_service = AuthService()