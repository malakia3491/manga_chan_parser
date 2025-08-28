from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from persistance.models.BaseModel import Base

class WorkTranslator(Base):
    __tablename__ = 'work_translators'
    work_id = Column(UUID(as_uuid=True), ForeignKey('works.id'), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)

    work = relationship("Work", back_populates="work_translators", lazy='selectin')
    user = relationship("User", back_populates="work_translations", lazy='selectin')