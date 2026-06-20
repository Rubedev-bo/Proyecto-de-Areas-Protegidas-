import pytest
from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    """Crea la app en modo testing."""
    _app = create_app("testing")
    with _app.app_context():
        _db.create_all()
        yield _app
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Registra un usuario y retorna headers con JWT."""
    client.post("/api/v1/auth/register", json={
        "nombre": "Test",
        "apellido": "User",
        "email": "test@upea.bo",
        "password": "segura123",
        "password_confirm": "segura123",
    })
    resp = client.post("/api/v1/auth/login", json={
        "email": "test@upea.bo",
        "password": "segura123",
    })
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestRegister:
    def test_registro_exitoso(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "nombre": "Ana",
            "apellido": "Quispe",
            "email": "ana@upea.bo",
            "password": "segura123",
            "password_confirm": "segura123",
        })
        assert resp.status_code == 201
        assert "usuario" in resp.get_json()

    def test_registro_email_duplicado(self, client):
        datos = {
            "nombre": "Luis",
            "apellido": "Copa",
            "email": "duplicado@upea.bo",
            "password": "segura123",
            "password_confirm": "segura123",
        }
        client.post("/api/v1/auth/register", json=datos)
        resp = client.post("/api/v1/auth/register", json=datos)
        assert resp.status_code == 422

    def test_registro_contrasenas_no_coinciden(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "nombre": "Pedro",
            "apellido": "Lima",
            "email": "pedro@upea.bo",
            "password": "segura123",
            "password_confirm": "diferente",
        })
        assert resp.status_code in (400, 422)


class TestLogin:
    def test_login_exitoso(self, client):
        client.post("/api/v1/auth/register", json={
            "nombre": "Login",
            "apellido": "Test",
            "email": "login@upea.bo",
            "password": "segura123",
            "password_confirm": "segura123",
        })
        resp = client.post("/api/v1/auth/login", json={
            "email": "login@upea.bo",
            "password": "segura123",
        })
        data = resp.get_json()
        assert resp.status_code == 200
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_credenciales_incorrectas(self, client):
        resp = client.post("/api/v1/auth/login", json={
            "email": "noexiste@upea.bo",
            "password": "mal",
        })
        assert resp.status_code == 401


class TestPerfil:
    def test_me_sin_token(self, client):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    def test_me_con_token(self, client, auth_headers):
        resp = client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert "usuario" in resp.get_json()
