from app.models.usuario import Usuario
from app.repositories.base_repository import BaseRepository
from app.extensions import db


class UsuarioRepository(BaseRepository[Usuario]):

    model = Usuario

    def get_by_email(self, email: str) -> Usuario | None:
        return (
            db.session.query(Usuario)
            .filter_by(email=email.lower().strip())
            .first()
        )

    def email_existe(self, email: str) -> bool:
        return self.exists(email=email.lower().strip())


usuario_repo = UsuarioRepository()