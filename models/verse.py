from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from .chapter import Chapter, Base
from .subchapter import Subchapter


class Verse(Base):
    __tablename__ = "verses"

    id = Column(Integer, primary_key=True, index=True)
    verse_num = Column(Integer, index=True)
    text = Column(String)
    chapter_id = Column(Integer, ForeignKey("chapters.id"))
    subchapter_id = Column(Integer, ForeignKey("subchapters.id"))

    chapter = relationship(Chapter, back_populates="verses")
    subchapter = relationship(Subchapter, back_populates="verses")
