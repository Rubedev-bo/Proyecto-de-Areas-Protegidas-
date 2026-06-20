from geoalchemy2.functions import ST_Within
from sqlalchemy import func
from app.extensions import db
from app.models.area_protegida import AreaProtegida


class AreaProtegidaRepository:

    model = AreaProtegida

    # ── Lectura básica ───────────────────────────────────────────

    def get_by_id(self, id: int) -> AreaProtegida | None:
        return db.session.get(AreaProtegida, id)

    def get_todas(self) -> list[AreaProtegida]:
        """Retorna todas las áreas (tu tabla no tiene columna `activa`)."""
        return (
            db.session.query(AreaProtegida)
            .order_by(AreaProtegida.nombre)
            .all()
        )

    def get_geojson_por_id(self, area_id: int):
        """
        Retorna (AreaProtegida, geojson_str, centroide_json_str)
        usando ST_AsGeoJSON y ST_Centroid calculados al vuelo
        (tu tabla no tiene columna `centroide` propia).
        """
        return (
            db.session.query(
                AreaProtegida,
                func.ST_AsGeoJSON(AreaProtegida.geom).label("geojson"),
                func.ST_AsGeoJSON(
                    func.ST_Centroid(AreaProtegida.geom)
                ).label("centroide_json"),
            )
            .filter(AreaProtegida.id == area_id)
            .first()
        )

    # ── Consultas espaciales (PostGIS) ──────────────────────────

    def get_area_que_contiene_punto(
        self, latitud: float, longitud: float
    ) -> AreaProtegida | None:
        """Retorna el área protegida que contiene el punto (lat, lon)."""
        punto = func.ST_SetSRID(func.ST_MakePoint(longitud, latitud), 4326)
        return (
            db.session.query(AreaProtegida)
            .filter(ST_Within(punto, AreaProtegida.geom))
            .first()
        )

    def get_areas_proximas(
        self, latitud: float, longitud: float, radio_km: float = 50
    ) -> list[AreaProtegida]:
        """Áreas dentro de `radio_km` km del punto (usando geography)."""
        radio_metros = radio_km * 1000
        punto = func.ST_SetSRID(func.ST_MakePoint(longitud, latitud), 4326)
        return (
            db.session.query(AreaProtegida)
            .filter(
                func.ST_DWithin(
                    func.cast(AreaProtegida.geom, db.String),
                    punto,
                    radio_metros,
                    True,
                )
            )
            .all()
        )

    def calcular_superficie_ha_postgis(self, area_id: int) -> float | None:
        """
        Calcula superficie real desde la geometría (en hectáreas).
        Útil para comparar contra la columna `Sup_Ha` ya existente
        y detectar discrepancias de digitalización.
        """
        result = (
            db.session.query(
                func.ST_Area(func.cast(AreaProtegida.geom, db.String)) / 10000
            )
            .filter(AreaProtegida.id == area_id)
            .scalar()
        )
        return float(result) if result else None

    def get_con_conteo_avistamientos(self) -> list:
        """Áreas con conteo de avistamientos (JOIN + GROUP BY)."""
        from app.models.avistamiento import Avistamiento

        return (
            db.session.query(
                AreaProtegida,
                func.count(Avistamiento.id).label("total_avistamientos"),
            )
            .outerjoin(
                Avistamiento,
                Avistamiento.area_protegida_id == AreaProtegida.id,
            )
            .group_by(AreaProtegida.id)
            .order_by(AreaProtegida.nombre)
            .all()
        )

    def buscar_por_nombre(self, texto: str) -> list[AreaProtegida]:
        """Búsqueda parcial por nombre (case-insensitive)."""
        return (
            db.session.query(AreaProtegida)
            .filter(AreaProtegida.nombre.ilike(f"%{texto}%"))
            .all()
        )

    def buscar_por_categoria(self, categoria: str) -> list[AreaProtegida]:
        return (
            db.session.query(AreaProtegida)
            .filter(AreaProtegida.categoria == categoria)
            .all()
        )


area_protegida_repo = AreaProtegidaRepository()