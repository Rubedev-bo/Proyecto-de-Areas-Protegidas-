import json
from app.repositories.area_protegida_repository import area_protegida_repo
from app.schemas.area_protegida_schema import area_schema, area_resumen_schema


class AreaProtegidaService:

    def listar_areas(self) -> list[dict]:
        resultados = area_protegida_repo.get_con_conteo_avistamientos()

        areas_serializadas = []
        for area, total in resultados:
            datos = area_resumen_schema.dump(area)
            datos["total_avistamientos"] = total
            areas_serializadas.append(datos)

        return areas_serializadas

    def obtener_area(self, area_id: int) -> dict:
        resultado = area_protegida_repo.get_geojson_por_id(area_id)
        if not resultado:
            raise ValueError(f"Área protegida con id={area_id} no encontrada.")

        area, geojson_str, centroide_str = resultado

        datos = area_schema.dump(area)
        datos["geojson"] = json.loads(geojson_str) if geojson_str else None
        datos["centroide_latlon"] = self._parse_centroide(centroide_str)

        return datos

    def identificar_area_por_punto(self, latitud: float, longitud: float) -> dict | None:
        area = area_protegida_repo.get_area_que_contiene_punto(latitud, longitud)
        if not area:
            return None
        return area_schema.dump(area)

    def buscar_por_nombre(self, texto: str) -> list[dict]:
        areas = area_protegida_repo.buscar_por_nombre(texto)
        return area_resumen_schema  # placeholder si decides usar many=True aparte

    def _parse_centroide(self, geojson_str: str | None) -> list[float] | None:
        if not geojson_str:
            return None
        try:
            data = json.loads(geojson_str)
            coords = data.get("coordinates", [])
            if len(coords) >= 2:
                return [round(coords[1], 6), round(coords[0], 6)]  # [lat, lon]
        except Exception:
            pass
        return None


area_protegida_service = AreaProtegidaService()