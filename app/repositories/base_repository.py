from typing import TypeVar, Generic, Type, Optional
from app.extensions import db
from app.models.base import BaseModel

T = TypeVar("T", bound=BaseModel)

class BaseRepository(Generic[T]):
    
    
    model: Type[T]
    
    # ── Lectura ───────────────────────────────────────────────────
    def get_by_id(self, id: int) -> Optional[T]:
        """Retorna el registro por PK o None."""
        return db.session.get(self.model, id)

    def get_all(self, activo: bool | None = None) -> list[T]:
        """Retorna todos los registros. Filtra por `activo` si el modelo lo tiene."""
        query = db.session.query(self.model)
        if activo is not None and hasattr(self.model, "activo"):
            query = query.filter_by(activo=activo)
        return query.all()

    def get_paginated(
        self,
        page: int = 1,
        per_page: int = 20,
        **filters,
    ):
        """Retorna página de resultados. `filters` se aplican con filter_by."""
        return (
            db.session.query(self.model)
            .filter_by(**filters)
            .paginate(page=page, per_page=per_page, error_out=False)
        )

    def get_by(self, **kwargs) -> Optional[T]:
        """Retorna el primer registro que coincida con los filtros."""
        return db.session.query(self.model).filter_by(**kwargs).first()

    def exists(self, **kwargs) -> bool:
        """Retorna True si existe al menos un registro con los filtros."""
        return db.session.query(
            db.session.query(self.model).filter_by(**kwargs).exists()
        ).scalar()

    # ── Escritura ─────────────────────────────────────────────────

    def create(self, **kwargs) -> T:
        """Crea un nuevo registro y hace commit."""
        instance = self.model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        db.session.refresh(instance)
        return instance

    def update(self, instance: T, **kwargs) -> T:
        """Actualiza los campos indicados y hace commit."""
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        db.session.commit()
        db.session.refresh(instance)
        return instance

    def delete(self, instance: T) -> None:
        """Elimina el registro y hace commit."""
        db.session.delete(instance)
        db.session.commit()

    def bulk_create(self, instances: list[T]) -> list[T]:
        """Inserta múltiples registros en una sola transacción."""
        db.session.bulk_save_objects(instances)
        db.session.commit()
        return instances

    # ── Sesión ────────────────────────────────────────────────────

    def flush(self) -> None:
        """Flush sin commit (para operaciones encadenadas)."""
        db.session.flush()

    def rollback(self) -> None:
        """Deshace la transacción actual."""
        db.session.rollback()