import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from persistance.models.BaseModel import Base

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True)
    
    works = association_proxy('work_tags', 'work')
    work_tags = relationship("WorkTag", back_populates="tag", cascade="all, delete-orphan", lazy='selectin')