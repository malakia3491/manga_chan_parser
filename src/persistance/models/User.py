import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy

from persistance.models.BaseModel import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    
    work_translations = relationship("WorkTranslator", back_populates="user", cascade="all, delete-orphan", lazy='selectin') 
    translated_chapters = association_proxy('work_translations', 'work')