from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from persistance.models.BaseModel import Base

class WorkTag(Base):
    __tablename__ = 'work_tags'
    work_id = Column(UUID(as_uuid=True), ForeignKey('works.id'), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey('tags.id'), primary_key=True)

    work = relationship("Work", back_populates="work_tags", lazy='selectin')
    tag = relationship("Tag", back_populates="work_tags", lazy='selectin')