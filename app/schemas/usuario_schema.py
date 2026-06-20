from marshmallow import Schema, fields, validate, validates, ValidationError, post_load
from app.models.usuario import Usuario


class UsuarioSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    apellido = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    rol = fields.Str(dump_only=True)
    activo = fields.Bool(dump_only=True)
    nombre_completo = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True, format="iso")
    updated_at = fields.DateTime(dump_only=True, format="iso")
    
        
        
class UsuarioCreateSchema(Schema):
    nombre = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    apellido = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        load_only=True,  # jamás serializar de vuelta
        validate=validate.Length(min=8, max=128),
    )
    password_confirm = fields.Str(required=True, load_only=True)
    rol = fields.Str(
        load_default="visitante",
        validate=validate.OneOf(["admin", "investigador", "visitante"]),
    )
    
    @validates("email")
    def validate_email_unico(self, value: str) -> None:
        from app.models.usuario import Usuario
        from app.extensions import db
        if db.session.query(Usuario).filter_by(email=value.lower()).first():
            raise ValidationError("Ya existe un usuario con este correo electrónico.")

    def validate(self, data: dict, **kwargs) -> dict:
        """Verifica que las contraseñas coincidan."""
        errors = {}
        if data.get("password") != data.get("password_confirm"):
            errors["password_confirm"] = ["Las contraseñas no coinciden."]
        if errors:
            raise ValidationError(errors)
        return data
    
    
class UsuarioUpdateSchema(Schema):
    """Esquema para actualización parcial (PATCH)."""

    nombre = fields.Str(validate=validate.Length(min=2, max=100))
    apellido = fields.Str(validate=validate.Length(min=2, max=100))
    email = fields.Email()


class LoginSchema(Schema):
    """Esquema para validar credenciales de login."""

    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    recordarme = fields.Bool(load_default=False)
    

# ── Instancias pre-configuradas (singleton) ───────────────────────────────────
usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)
usuario_create_schema = UsuarioCreateSchema()
usuario_update_schema = UsuarioUpdateSchema()
login_schema = LoginSchema()