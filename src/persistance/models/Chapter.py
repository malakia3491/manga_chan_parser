import uuid
from sqlalchemy import UUID, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from persistance.models.BaseModel import Base

class Chapter(Base):
    __tablename__ = 'chapters'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    work_id = Column(UUID(as_uuid=True), ForeignKey('works.id'), nullable=False)
    parsing_session_id = Column(UUID(as_uuid=True), ForeignKey('parsing_sessions.id'))
    
    number = Column(Integer)
    content_path = Column(String, nullable=False)
    download_url = Column(String)
    
    work = relationship("Work", back_populates="chapters", lazy='selectin')
    parsing_session = relationship("ParsingSession", back_populates="chapters", lazy='selectin')