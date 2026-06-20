from geoalchemy2 import Geometry
from app.extensions import db, Column
from app.models.base import BaseModel

class Avistamiento(BaseModel):
    __tablename__ = "avistamientos"
    
    # ── Taxonomía ─────────────────────────────────────────────────
    especie = Column(db.String(255), nullable=False, index=True)
    nombre_comun = Column(db.String(255), nullable=True)
    reino = Column(db.String(100), nullable=True)
    filo = Column(db.String(100), nullable=True)
    clase = Column(db.String(100), nullable=True)
    orden = Column(db.String(100), nullable=True)
    familia = Column(db.String(100), nullable=True)
    genero = Column(db.String(100), nullable=True)
    
    
    # ── Observación ───────────────────────────────────────────────
    fecha_observacion = Column(db.Date, nullable=True)
    observador = Column(db.String(255), nullable=True)
    cantidad = Column(db.Integer, nullable=True, default=1)
    notas = Column(db.Text, nullable=True)
    
    
    # ── Fuente de datos ───────────────────────────────────────────
    fuente = Column(
        db.Enum("gbif", "manual", "sernap", "otro", name="fuente_avistamiento"),
        nullable=False,
        default="manual",
    )
    gbif_occurrence_key = Column(db.BigInteger, nullable=True, unique=True)
    
    # ── Campo geoespacial (PostGIS) ───────────────────────────────
    #   POINT en WGS 84 (longitud, latitud).
    ubicacion = Column(
        Geometry(geometry_type="POINT", srid=4326),
        nullable=False,
    )
    
    
    # ── Coordenadas desnormalizadas (para consultas rápidas sin PostGIS) ──
    latitud = Column(db.Numeric(10, 7), nullable=True)
    longitud = Column(db.Numeric(10, 7), nullable=True)
    
    
    # ── Claves foráneas ───────────────────────────────────────────
    area_protegida_id = Column(
        db.Integer,
        db.ForeignKey("areas_protegidas.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    usuario_id = Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    
    # ── Relaciones ────────────────────────────────────────────────
    area_protegida = db.relationship(
        "AreaProtegida",
        back_populates="avistamientos",
    )
    registrado_por = db.relationship(
        "Usuario",
        back_populates="avistamientos",
    )

    def __repr__(self) -> str:
        return (
            f"<Avistamiento id={self.id} especie='{self.especie}' "
            f"lat={self.latitud} lon={self.longitud}>"
        )