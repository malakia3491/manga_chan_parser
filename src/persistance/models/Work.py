import uuid
from sqlalchemy import UUID, Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from persistance.models.WorkAuthor import WorkAuthor
from persistance.models.WorkTag import WorkTag
from persistance.models.WorkTranslator import WorkTranslator
from persistance.models.BaseModel import Base

class Work(Base):
    __tablename__ = 'works'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    series_id = Column(UUID(as_uuid=True), ForeignKey('series.id'), nullable=True)

    type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    page_url = Column(String)

    series = relationship("Series", back_populates="works", lazy='selectin')

    work_authors = relationship(
        "WorkAuthor",
        back_populates="work",
        cascade="all, delete-orphan",
        lazy='selectin'
    )

    authors = association_proxy(
        'work_authors', 'author',
        creator=lambda author: WorkAuthor(author_id=author.id)
    )

    work_tags = relationship(
        "WorkTag",
        back_populates="work",
        cascade="all, delete-orphan",
        lazy='selectin'
    )
    tags = association_proxy(
        'work_tags', 'tag',
        creator=lambda tag: WorkTag(tag_id=tag.id)
    )

    chapters = relationship(
        "Chapter",
        back_populates="work",
        cascade="all, delete-orphan",
        lazy='selectin'
    )

    work_translators = relationship(
        "WorkTranslator",
        back_populates="work",
        cascade="all, delete-orphan",
        lazy='selectin'
    )
    
    translators = association_proxy(
        'work_translators', 'user',
        creator=lambda user: WorkTranslator(user_id=user.id)
    )