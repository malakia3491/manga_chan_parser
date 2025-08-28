from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from persistance.models.BaseModel import Base

class WorkAuthor(Base):
    __tablename__ = 'work_authors'
    work_id = Column(UUID(as_uuid=True), ForeignKey('works.id'), primary_key=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey('authors.id'), primary_key=True)

    work = relationship("Work", back_populates="work_authors", lazy='selectin')
    author = relationship("Author", back_populates="work_authors", lazy='selectin')