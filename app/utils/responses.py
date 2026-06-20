from flask import jsonify
from typing import Any


def success(data: Any = None, mensaje: str = "OK", status: int = 200):
    """Respuesta exitosa estándar."""
    body = {"status": "success", "mensaje": mensaje}
    if data is not None:
        body["data"] = data
    return jsonify(body), status


def created(data: Any = None, mensaje: str = "Recurso creado."):
    return success(data=data, mensaje=mensaje, status=201)


def error(mensaje: str, detalle: Any = None, status: int = 400):
    """Respuesta de error estándar."""
    body = {"status": "error", "mensaje": mensaje}
    if detalle is not None:
        body["detalle"] = detalle
    return jsonify(body), status


def not_found(recurso: str = "Recurso"):
    return error(f"{recurso} no encontrado.", status=404)


def forbidden(mensaje: str = "Acceso denegado."):
    return error(mensaje, status=403)


def validation_error(errores: dict):
    return error("Datos inválidos.", detalle=errores, status=422)


def paginated(items: list, total: int, page: int, pages: int, per_page: int):
    """Respuesta paginada estándar."""
    return jsonify({
        "status": "success",
        "paginacion": {
            "total": total,
            "pagina": page,
            "paginas": pages,
            "por_pagina": per_page,
        },
        "data": items,
    }), 200
