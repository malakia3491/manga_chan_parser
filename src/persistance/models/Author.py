import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy

from persistance.models.BaseModel import Base

class Author(Base):
    __tablename__ = 'authors'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True)
    
    works = association_proxy('work_authors', 'work')
    work_authors = relationship("WorkAuthor", back_populates="author", cascade="all, delete-orphan", lazy='selectin')