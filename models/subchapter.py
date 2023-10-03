from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .book import Base


class Subchapter(Base):
    __tablename__ = "subchapters"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True)

    verses = relationship("Verse", back_populates="subchapter")
