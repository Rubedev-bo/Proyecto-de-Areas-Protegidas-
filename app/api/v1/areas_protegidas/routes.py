from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from app.services.area_protegida_service import area_protegida_service

areas_bp = Blueprint("areas_protegidas", __name__)


@areas_bp.get("/")
def listar_areas():
    pass