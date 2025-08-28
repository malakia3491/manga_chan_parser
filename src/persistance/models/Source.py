from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from persistance.models.BaseModel import Base

class Source(Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    destination = Column(String)
    
    parsing_sessions = relationship("ParsingSession", back_populates="source", lazy='selectin')
    domains = relationship("Domain", back_populates="source", lazy='selectin')