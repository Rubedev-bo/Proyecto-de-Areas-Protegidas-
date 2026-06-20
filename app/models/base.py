from datetime import datetime, timezone
from app.extensions import db, Column



class BaseModel(db.Model):
    __abstract__ = True
    
    id = Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
        )
    create_at = Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    update_at = Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        
    )
    
    def save(self) -> "BaseModel":
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self) -> dict:
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
        }
        
    def __rep__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"