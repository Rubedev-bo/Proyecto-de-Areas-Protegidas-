import requests
from flask import current_app
from app.extensions import db
from app.models.avistamiento import Avistamiento
from app.repositories.area_protegida_repository import area_protegida_repo


BOLIVIA_COUNTRY_CODE = "BO"


class GBIFService:
    """Integración con la API REST de GBIF."""

    @property
    def base_url(self) -> str:
        return current_app.config.get("GBIF_API_BASE_URL", "https://api.gbif.org/v1")

    def buscar_ocurrencias(
        self,
        especie: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        """
        Busca ocurrencias de especies en Bolivia.

        Args:
            especie: nombre científico (opcional).
            limit: cantidad de resultados (máx 300 en GBIF).
            offset: paginación.

        Returns:
            dict con 'results' y metadatos de paginación.
        """
        params = {
            "country": BOLIVIA_COUNTRY_CODE,
            "hasCoordinate": True,
            "hasGeospatialIssue": False,
            "limit": min(limit, 300),
            "offset": offset,
        }
        if especie:
            params["scientificName"] = especie

        response = requests.get(
            f"{self.base_url}/occurrence/search",
            params=params,
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    def importar_ocurrencias_bolivia(
        self,
        especie: str | None = None,
        limite: int = 50,
    ) -> dict:
        """
        Importa ocurrencias de GBIF y las guarda en la BD local.
        Asocia automáticamente con el área protegida correspondiente
        usando ST_Within de PostGIS.

        Returns:
            dict con conteos de importación.
        """
        datos_gbif = self.buscar_ocurrencias(especie=especie, limit=limite)
        resultados = datos_gbif.get("results", [])

        creados = 0
        duplicados = 0
        sin_coordenadas = 0

        for registro in resultados:
            # Filtrar registros sin coordenadas
            lat = registro.get("decimalLatitude")
            lon = registro.get("decimalLongitude")
            if lat is None or lon is None:
                sin_coordenadas += 1
                continue

            gbif_key = registro.get("key")

            # Evitar duplicados
            existente = (
                db.session.query(Avistamiento)
                .filter_by(gbif_occurrence_key=gbif_key)
                .first()
            )
            if existente:
                duplicados += 1
                continue

            # Determinar área protegida por intersección espacial
            area = area_protegida_repo.get_area_que_contiene_punto(lat, lon)

            # Construir geometría POINT en formato WKT
            punto_wkt = f"SRID=4326;POINT({lon} {lat})"

            avistamiento = Avistamiento(
                especie=registro.get("scientificName", "Desconocida"),
                nombre_comun=registro.get("vernacularName"),
                reino=registro.get("kingdom"),
                filo=registro.get("phylum"),
                clase=registro.get("class"),
                orden=registro.get("order"),
                familia=registro.get("family"),
                genero=registro.get("genus"),
                latitud=lat,
                longitud=lon,
                ubicacion=punto_wkt,
                fuente="gbif",
                gbif_occurrence_key=gbif_key,
                area_protegida_id=area.id if area else None,
            )

            db.session.add(avistamiento)
            creados += 1

        db.session.commit()

        return {
            "importados": creados,
            "duplicados": duplicados,
            "sin_coordenadas": sin_coordenadas,
            "total_procesados": len(resultados),
        }


# ── Instancia singleton ───────────────────────────────────────────────────────
gbif_service = GBIFService()