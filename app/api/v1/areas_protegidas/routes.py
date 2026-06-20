from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from app.services.area_protegida_service import area_protegida_service

areas_bp = Blueprint("areas_protegidas", __name__)


# ── GET / ─────────────────────────────────────────────────────────────────────

@areas_bp.get("/")
def listar_areas():
    """
    Lista todas las áreas protegidas activas con conteo de avistamientos.
    No requiere autenticación (información pública).
    """
    try:
        areas = area_protegida_service.listar_areas()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "total": len(areas),
        "areas": areas,
    }), 200


# ── GET /<id> ─────────────────────────────────────────────────────────────────

@areas_bp.get("/<int:area_id>")
def obtener_area(area_id: int):
    """Retorna el detalle de un área con su polígono en GeoJSON."""
    try:
        area = area_protegida_service.obtener_area(area_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(area), 200


# ── GET /punto?lat=&lon= ──────────────────────────────────────────────────────

@areas_bp.get("/punto")
def area_por_punto():
    """
    Determina qué área protegida contiene el punto (lat, lon).
    Usa ST_Within de PostGIS.

    Query params:
        lat: latitud decimal (ej: -16.5)
        lon: longitud decimal (ej: -68.1)
    """
    try:
        lat = float(request.args.get("lat", ""))
        lon = float(request.args.get("lon", ""))
    except (TypeError, ValueError):
        return jsonify({"error": "Parámetros lat y lon son requeridos y deben ser numéricos."}), 400

    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return jsonify({"error": "Coordenadas fuera de rango."}), 400

    try:
        area = area_protegida_service.identificar_area_por_punto(lat, lon)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if area is None:
        return jsonify({
            "dentro_de_area": False,
            "mensaje": "El punto no está dentro de ningún área protegida.",
        }), 200

    return jsonify({
        "dentro_de_area": True,
        "area": area,
    }), 200