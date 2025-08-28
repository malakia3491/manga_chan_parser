import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from persistance.models.BaseModel import Base

class Series(Base):
    __tablename__ = 'series'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True)
    
    works = relationship("Work", back_populates="series", lazy='selectin')