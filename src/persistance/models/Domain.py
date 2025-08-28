from sqlalchemy import Column, ForeignKey, String, Integer
from sqlalchemy.orm import relationship

from persistance.models.BaseModel import Base

class Domain(Base):
    __tablename__ = 'domains'
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('sources.id'))
    address = Column(String, unique=True)
    
    source = relationship("Source", back_populates="domains", lazy='selectin')