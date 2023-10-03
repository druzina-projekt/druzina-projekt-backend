from models import Book, Chapter, Subchapter, Verse
from .configure import es


def index_book(book: Book):
    doc = {
        'book_num': book.book_num,
        'title': book.title,
    }
    es.index(index='books', id=book.id, body=doc)


def index_chapter(chapter: Chapter, book: Book):
    doc = {
        'chapter_num': chapter.chapter_num,
        'book_id': book.id
    }
    es.index(index='chapters', id=chapter.id, body=doc)


def index_subchapter(subchapter: Subchapter):
    doc = {
        'title': subchapter.title
    }
    es.index(index='subchapters', id=subchapter.id, body=doc)


def index_verse(verse: Verse, chapter: Chapter, subchapter: Subchapter):
    doc = {
        'verse_num': verse.verse_num,
        'text': verse.text,
        'chapter_id': chapter.id,
        'subchapter_id': subchapter.id
    }
    es.index(index='verses', id=verse.id, body=doc)
