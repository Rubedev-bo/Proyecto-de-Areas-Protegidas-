import os 
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY : str = os.getenv("SECRET_KEY","llavesecretainsegura")
    WTF_CSRF_ENABLED : bool = True
    
    SQLALCHEMY_DATABASE_URI : str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:system@localhost:5433/areas_protegidas"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS : bool = False
    SQLALCHEMY_ECHO: bool = False
    
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret")
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(days=30)
    JWT_TOKEN_LOCATION: list = ["headers"]
    JWT_HEADER_NAME: str = "Authorization"
    JWT_HEADER_TYPE: str = "Bearer"
    
    LOGIN_DISABLED: bool = False
    REMEMBER_COOKIE_DURATION: timedelta = timedelta(minutes=30)
    
    
    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000"
    ).split(",")
    
    GBIF_API_BASE_URL: str = os.getenv(
        "GBIF_API_BASE_URL", "https://api.gbif.org/v1"
    )
    
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    

class DevelopmentConfig(Config):
    """Configuración para desarrollo local."""

    DEBUG: bool = True
    SQLALCHEMY_ECHO: bool = True          # Ver SQL generado en desarrollo
    WTF_CSRF_ENABLED: bool = False  
    


class TestingConfig(Config):
    """Configuración para pruebas automáticas."""

    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/gis_test",
    )
    WTF_CSRF_ENABLED: bool = False
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(minutes=5)
    
    
class ProductionConfig(Config):
    """Configuración para producción."""

    DEBUG: bool = False
    TESTING: bool = False
    SQLALCHEMY_ECHO: bool = False

    # En producción la SECRET_KEY DEBE venir de la variable de entorno
    SECRET_KEY: str = os.environ["SECRET_KEY"]          # KeyError intencional
    JWT_SECRET_KEY: str = os.environ["JWT_SECRET_KEY"]
    
    

config_map: dict = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config(env_name: str | None = None) -> Config:
    """Retorna la clase de configuración correspondiente al entorno."""
    env = env_name or os.getenv("FLASK_ENV", "default")
    return config_map.get(env, DevelopmentConfig)
