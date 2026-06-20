from marshmallow import Schema, fields


class AreaProtegidaSchema(Schema):
    """Esquema completo con GeoJSON."""

    id = fields.Int(dump_only=True)
    codigo_ap = fields.Int(allow_none=True)
    nombre = fields.Str(allow_none=True)
    categoria = fields.Str(allow_none=True)
    nivel = fields.Str(allow_none=True)
    cod_sdsn = fields.Str(allow_none=True)
    sup_ha = fields.Float(allow_none=True)
    fecha = fields.Date(allow_none=True)
    creacion = fields.Str(allow_none=True)
    base_legal = fields.Str(allow_none=True)

    # Calculados en el servicio, no son columnas de la tabla
    geojson = fields.Dict(dump_only=True, allow_none=True)
    centroide_latlon = fields.List(fields.Float(), dump_only=True, allow_none=True)
    total_avistamientos = fields.Int(dump_only=True, allow_none=True)


class AreaProtegidaResumenSchema(Schema):
    """Esquema reducido para listados (sin geometría completa)."""

    id = fields.Int(dump_only=True)
    codigo_ap = fields.Int(allow_none=True)
    nombre = fields.Str(allow_none=True)
    categoria = fields.Str(allow_none=True)
    nivel = fields.Str(allow_none=True)
    sup_ha = fields.Float(allow_none=True)
    centroide_latlon = fields.List(fields.Float(), allow_none=True)
    total_avistamientos = fields.Int(allow_none=True)


area_schema = AreaProtegidaSchema()
areas_schema = AreaProtegidaSchema(many=True)
area_resumen_schema = AreaProtegidaResumenSchema()
areas_resumen_schema = AreaProtegidaResumenSchema(many=True)