from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .book import Book, Base


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    chapter_num = Column(Integer, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))

    verses = relationship("Verse", back_populates="chapter")
    book = relationship(Book, back_populates="chapters")
