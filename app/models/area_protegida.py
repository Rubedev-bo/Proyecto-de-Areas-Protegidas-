from geoalchemy2 import Geometry
from app.extensions import db, Column

class AreaProtegida(db.Model):
    __tablename__ = "areas_protegidas"
    
    id = Column(db.Integer, primary_key=True, autoincrement=True)
    geom = Column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326), 
        nullable=False,
        )
    
    
    codigo_ap = db.Column("CodigoAP", db.BigInteger, nullable=True)
    fecha = db.Column("Fecha", db.Date, nullable=True)
    sup_ha = db.Column("Sup_Ha", db.Float, nullable=True)
    creacion = db.Column("CREACION", db.String, nullable=True)
    nivel = db.Column("NIVEL", db.String, nullable=True)
    cod_sdsn = db.Column("Cod_SDSN", db.String, nullable=True)
    nombre = db.Column("NOMBRE", db.String, nullable=True, index=True)
    categoria = db.Column("CATEGORIA", db.String, nullable=True)
    base_legal = db.Column("BASE_LEGAL", db.String, nullable=True)
    
    avistamientos = db.relationship(
        "Avistamiento",
        back_populates="area_protegida",
        lazy="dynamic",
    )
    
    def to_dict(self) -> dict:
        """Serialización básica sin geometría (para listados)."""
        return {
            "id": self.id,
            "codigo_ap": self.codigo_ap,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "nivel": self.nivel,
            "sup_ha": self.sup_ha,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "creacion": self.creacion,
            "cod_sdsn": self.cod_sdsn,
            "base_legal": self.base_legal,
        }

    def __repr__(self) -> str:
        return f"<AreaProtegida id={self.id} nombre='{self.nombre}'>"