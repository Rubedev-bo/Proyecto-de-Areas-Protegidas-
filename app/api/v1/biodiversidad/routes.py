from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from app.services.gbif_service import gbif_service
from app.extensions import db
from app.models.avistamiento import Avistamiento
from app.repositories.area_protegida_repository import area_protegida_repo

biodiversidad_bp = Blueprint("biodiversidad", __name__)


# ── GET / ─────────────────────────────────────────────────────────────────────

@biodiversidad_bp.get("/")
def listar_avistamientos():
    """
    Lista avistamientos con filtros opcionales.

    Query params:
        especie: filtrar por nombre científico (LIKE)
        area_id: filtrar por área protegida
        fuente:  gbif | manual
        page:    número de página (default 1)
        per_page: resultados por página (default 20)
    """
    especie = request.args.get("especie")
    area_id = request.args.get("area_id", type=int)
    fuente = request.args.get("fuente")
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)

    query = db.session.query(Avistamiento)

    if especie:
        query = query.filter(Avistamiento.especie.ilike(f"%{especie}%"))
    if area_id:
        query = query.filter_by(area_protegida_id=area_id)
    if fuente:
        query = query.filter_by(fuente=fuente)

    paginado = query.order_by(Avistamiento.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    resultados = [
        {
            "id": a.id,
            "especie": a.especie,
            "nombre_comun": a.nombre_comun,
            "latitud": float(a.latitud) if a.latitud else None,
            "longitud": float(a.longitud) if a.longitud else None,
            "fuente": a.fuente,
            "area_protegida_id": a.area_protegida_id,
            "fecha_observacion": a.fecha_observacion.isoformat() if a.fecha_observacion else None,
        }
        for a in paginado.items
    ]

    return jsonify({
        "total": paginado.total,
        "pagina": paginado.page,
        "paginas": paginado.pages,
        "por_pagina": per_page,
        "avistamientos": resultados,
    }), 200


# ── POST /importar-gbif ───────────────────────────────────────────────────────

@biodiversidad_bp.post("/importar-gbif")
@jwt_required()
def importar_gbif():
    """
    Importa registros de ocurrencias desde la API pública de GBIF.
    Solo accesible para investigadores y admins.

    Body (opcional):
        { "especie": "Vicugna vicugna", "limite": 100 }
    """
    # Verificar rol
    claims = get_jwt()
    if claims.get("rol") not in ("admin", "investigador"):
        return jsonify({"error": "No tienes permiso para importar datos."}), 403

    datos = request.get_json(silent=True) or {}
    especie = datos.get("especie")
    limite = min(datos.get("limite", 50), 300)

    try:
        resultado = gbif_service.importar_ocurrencias_bolivia(
            especie=especie, limite=limite
        )
    except Exception as e:
        return jsonify({"error": f"Error al conectar con GBIF: {str(e)}"}), 502

    return jsonify({
        "mensaje": "Importación completada.",
        "resultado": resultado,
    }), 200


# ── POST / (registro manual) ──────────────────────────────────────────────────

@biodiversidad_bp.post("/")
@jwt_required()
def registrar_avistamiento():
    """
    Registra un avistamiento manual georreferenciado.
    Determina automáticamente el área protegida usando PostGIS.

    Body:
        {
            "especie": "Panthera onca",
            "latitud": -14.5,
            "longitud": -61.2,
            "fecha_observacion": "2024-06-01",
            "notas": "Observado en el sendero norte"
        }
    """
    datos = request.get_json(silent=True) or {}
    usuario_id = int(get_jwt_identity())

    especie = datos.get("especie", "").strip()
    try:
        lat = float(datos["latitud"])
        lon = float(datos["longitud"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "latitud y longitud son requeridos."}), 400

    if not especie:
        return jsonify({"error": "El campo especie es requerido."}), 400

    # Detectar área protegida por ST_Within
    area = area_protegida_repo.get_area_que_contiene_punto(lat, lon)

    punto_wkt = f"SRID=4326;POINT({lon} {lat})"

    avistamiento = Avistamiento(
        especie=especie,
        nombre_comun=datos.get("nombre_comun"),
        latitud=lat,
        longitud=lon,
        ubicacion=punto_wkt,
        fuente="manual",
        notas=datos.get("notas"),
        area_protegida_id=area.id if area else None,
        usuario_id=usuario_id,
    )

    db.session.add(avistamiento)
    db.session.commit()

    return jsonify({
        "mensaje": "Avistamiento registrado.",
        "id": avistamiento.id,
        "area_protegida": area.nombre if area else None,
        "dentro_de_area": area is not None,
    }), 201