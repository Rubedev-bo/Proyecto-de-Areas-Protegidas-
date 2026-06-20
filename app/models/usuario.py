from flask_login import UserMixin
from app.extensions import db, bcrypt, login_manager, Column
from app.models.base import BaseModel


class RolUsuario(db.Enum):
    ADMIN = "admin"
    INVESTIGADOR = "investigador"
    VISITANTE = "visitante"
    
    
class Usuario(UserMixin, BaseModel):
    __tablename__ = "usuarios"
    
    # ── Campos ───────────────────────────────────────────────────
    nombre = Column(db.String(30), nullable=False)
    apellido = Column(db.String(60), nullable=False)
    email = Column(db.String(50), nullable=False, unique=True, index=True)
    _password_hash = Column("password_hash",db.String(255), nullable=False)
    
    rol = Column(
        db.Enum("admin", "investigador", "visitante", name="rol_usuario"),
        nullable=False,
        default="visitante",
    )
    activo = Column(db.Boolean, nullable=False, default=True)
    ultimo_acceso = Column(db.DateTime(timezone=True), nullable=True)
    
    
    # ── Relaciones ────────────────────────────────────────────────
    avistamientos = db.relationship(
        "Avistamiento",
        back_populates="registrado_por",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    
    # ── Propiedad password (write-only) 
    @property
    def password(self):
        raise AttributeError("La contraseña no es legible directamente.")
    
    @password.setter
    def password(self, plain_text: str) -> None:
        self._password_hash = bcrypt.generate_password_hash(plain_text).decode("utf-8")
        
    def verificar_password(self, plain_text: str) -> bool:
        return bcrypt.check_password_hash(self._password_hash, plain_text)
    
    
    # ── Flask-Login: active check ────────────────────────────────
    @property
    def is_active(self) -> bool:
        return self.activo
    
    # ── Helpers de rol ────────────────────────────────────────────
    def es_admin(self) -> bool:
        return self.rol == "admin"
    
    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"
    
    def __repr__(self) -> str:
        return f"<Usuario id={self.id} email={self.email} rol={self.rol}>"
    

# ── user_loader requerido por Flask-Login ─────────────────────────────────────
@login_manager.user_loader
def  load_user(user_id: str) -> Usuario | None:
    return db.session.get(Usuario, int(user_id))