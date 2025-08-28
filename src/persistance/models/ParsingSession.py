import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from persistance.models.BaseModel import Base

class ParsingSession(Base):
    __tablename__ = 'parsing_sessions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(Integer, ForeignKey('sources.id'))
    parsing_date = Column(DateTime)
    
    source = relationship("Source", back_populates="parsing_sessions", lazy='selectin')
    chapters = relationship("Chapter", back_populates="parsing_session", lazy='selectin')