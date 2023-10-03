import io
import re
from typing import Union, Tuple

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTTextLineHorizontal, LTChar
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import and_

from errors import ParseError
from models import Book, Chapter, Subchapter, Verse
from search import index_book, index_chapter, index_subchapter, index_verse

# TODO: Have to define constraints differently for the full PDF data file, because it will be too large.
#   Solution: rounding up the font size numbers?
IGNORE_TEXT_PROPERTIES_LIST = [
    (7.5, "WJFGOF+Dax-Medium"),
    (8.0, "HFMDRJ+WalbaumK-Bold"),
    (6.900000000000091, "RIDRBP+WalbaumK"),
    (10.0, "HFMDRJ+WalbaumK-Bold"),
    (6.900000000000034, "RIDRBP+WalbaumK"),
    (6.899999999999977, "RIDRBP+WalbaumK"),
    (6.900000000000006, "RIDRBP+WalbaumK"),
    (6.899999999999999, "RIDRBP+WalbaumK"),
    (8.0, "RIDRBP+WalbaumK"),
    (6.000000000000001, "WJFGOF+Helvetica"),
    (6.900000000000006, "WJFGOF+WalbaumK-Italic"),
    (6.900000000000006, "WIXHOF+WalbaumJSc"),
    (6.90000000000002, "RIDRBP+WalbaumK"),
    (8.000000000000057, "HFMDRJ+WalbaumK-Bold"),
    (7.999999999999993, "HFMDRJ+WalbaumK-Bold"),
    (6.90000000000002, "WJFGOF+WalbaumK-Italic"),
]

CHAPTER_TEXT_PROPERTIES_LIST = [
    (23.015600000000006, "HFMDRJ+WalbaumK-Bold"),
    (23.015599999999978, "HFMDRJ+WalbaumK-Bold"),
]

VERSE_TEXT_PROPERTIES_LIST = [
    (5.7999999999999545, "RIDRBP+WalbaumK"),
    (5.800000000000011, "RIDRBP+WalbaumK"),
    (10.0, "RIDRBP+WalbaumK"),
    (10.000000000000028, "RIDRBP+WalbaumK"),
    (9.999999999999943, "RIDRBP+WalbaumK"),
    (9.999999999999943, "RIDRBP+WalbaumK"),
    (5.799999999999983, "RIDRBP+WalbaumK"),
    (10.0, "WIXHOF+WalbaumJSc"),
]


class PDFParser:
    def __init__(self, db: Session):
        self.db = db
        self.book = None
        self.chapter = None
        self.subchapter = None
        self.verse_num = None
        self.verse = None

    def process_text_line(self, text_val: str, font_size: float, font_name: str):
        # TODO: Have to also parse books for the full PDF data file

        if self.is_chapter_beginning(font_size, font_name):
            chapter_num, verse_text = self.get_chapter(text_val)
            if chapter_num == 0:
                raise ParseError(detail=f"Could not parse chapter number for the following text line: '{text_val}'")
            self.add_chapter(chapter_num)
            self.handle_verse(verse_text)
            return

        if self.is_subchapter(font_size, font_name):
            subchapter_title = self.get_subchapter(text_val)
            if len(subchapter_title) == 0:
                raise ParseError(detail=f"Could not parse subchapter title for the following text line: '{text_val}'")
            self.add_subchapter(subchapter_title)
            return

        if self.is_verse(font_size, font_name):
            self.handle_verse(text_val)
            return

        raise ParseError(detail=f"Could not categorize the following text line: '{text_val}'")

    def add_chapter(self, chapter_num):
        self.db.commit()
        chapter = Chapter(chapter_num=chapter_num, book_id=self.book.id)
        self.chapter = chapter
        self.db.add(chapter)
        index_chapter(chapter, self.book)
        self.db.flush()

    def add_subchapter(self, subchapter_title):
        subchapter = Subchapter(title=subchapter_title)
        self.subchapter = subchapter
        self.db.add(subchapter)
        index_subchapter(subchapter)

    def handle_verse(self, text: str) -> None:
        parts = re.split(r'(?<=[.?!«»])\s|(?<=[.?!«»])\d', text)
        for part in parts:
            # Is number at the start of the text (beginning of verse)?
            match = re.match(r'(\d+)(.*)', part)

            if match:
                # We add the previous full verse to the database if it exists
                if self.check_verse_for_database_add():
                    verse_obj = Verse(
                        verse_num=self.verse_num,
                        text=self.verse,
                        chapter_id=self.chapter.id,
                        subchapter_id=self.subchapter.id
                    )
                    self.db.add(verse_obj)
                    index_verse(verse_obj, self.chapter, self.subchapter)

                # We set the new verse number and verse text
                verse_num, text = match.groups()
                self.verse_num = int(verse_num)
                self.verse = part
            else:
                # An error is thrown if there is no previously set text for the continued verse text
                if len(self.verse) == 0:
                    raise ParseError(detail=f"Error in parsing, there is no previously set verse for the following "
                                            f"verse continuation: '{part}'")

                # We handle the string concatenation based on the end of the already stored verse
                if self.verse[-1] == '-':
                    self.verse = self.verse + part
                else:
                    self.verse = self.verse + ' ' + part

    def check_verse_for_database_add(self) -> bool:
        if ((self.is_not_empty(self.verse)) and (self.verse_num is not None) and (self.chapter is not None)
                and (self.subchapter is not None)):
            return True
        return False

    @staticmethod
    def is_chapter_beginning(font_size: float, font_name: str) -> bool:
        if (font_size, font_name) in CHAPTER_TEXT_PROPERTIES_LIST:
            return True
        return False

    @staticmethod
    def is_subchapter(font_size: float, font_name: str) -> bool:
        if font_size == 10.0 and font_name == "HFMDRJ+WalbaumK-Bold":
            return True
        return False

    @staticmethod
    def is_verse(font_size: float, font_name: str) -> bool:
        if (font_size, font_name) in VERSE_TEXT_PROPERTIES_LIST:
            return True
        return False

    @staticmethod
    def get_chapter(text: str) -> Tuple[int, str]:
        first_val = text.split(" ", 1)[0]
        rest_of_text = text[len(first_val) + 1:]
        try:
            return int(first_val), rest_of_text
        except ValueError:
            pass
        return 0, rest_of_text

    @staticmethod
    def get_subchapter(text: str) -> str:
        return re.sub(r'\([^)]*\)', '', text).strip()

    @staticmethod
    def is_not_empty(text_val: Union[str, None]) -> bool:
        if (text_val is not None) and (len(text_val.strip()) != 0):
            return True
        return False


def check_text(text_val: str, font_size: float, font_name: str) -> bool:
    if (font_size, font_name) in IGNORE_TEXT_PROPERTIES_LIST:
        if font_size == 10.0 and font_name == "HFMDRJ+WalbaumK-Bold":
            try:
                float(text_val)
                return False
            except ValueError:
                pass
        else:
            return False
    return True


def parse_pdf(db: Session, pdf_bytes: bytes):
    try:
        pdf_file_io = io.BytesIO(pdf_bytes)

        # TODO: Remove when parsing the full PDF data file, because creation should be automatic for each book, chapter,
        #  subchapter and verse
        try:
            book = Book(book_num=1, title="PRVA MOJZESOVA KNJIGA (GENEZA)")
            db.add(book)
            index_book(book)
            db.commit()
            db.refresh(book)
        except IntegrityError:
            db.rollback()
            book = db \
                .query(Book) \
                .filter_by(book_num=1) \
                .first()

        try:
            chapter = Chapter(chapter_num=24, book_id=book.id)
            db.add(chapter)
            index_chapter(chapter, book)
            db.commit()
            db.refresh(chapter)
        except IntegrityError:
            db.rollback()
            chapter = db \
                .query(Chapter) \
                .filter(and_(Chapter.chapter_num == 24, Chapter.book_id == book.id)) \
                .first()

        try:
            subchapter = Subchapter(title="Abraham oženi Izaka")
            db.add(subchapter)
            index_subchapter(subchapter)
            db.commit()
            db.refresh(subchapter)
        except IntegrityError:
            db.rollback()
            subchapter = db \
                .query(Subchapter) \
                .filter_by(title="Abraham oženi Izaka") \
                .first()

        verse_num = 57

        parser = PDFParser(db)
        parser.book = book
        parser.chapter = chapter
        parser.subchapter = subchapter
        parser.verse_num = verse_num

        for page_layout in extract_pages(pdf_file_io):
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    for text_line in element:
                        if isinstance(text_line, LTTextLineHorizontal):
                            for character in text_line:
                                if isinstance(character, LTChar):
                                    text_val = text_line.get_text().strip()
                                    font_size = character.size
                                    font_name = character.fontname

                                    if check_text(text_val, font_size, font_name):
                                        print(f"Text: '{text_val}', "
                                              f"Font size: {font_size}, "
                                              f"Font name: {font_name}")
                                        parser.process_text_line(text_val, font_size, font_name)
                                        break
                                    break

        # Add the last verse and commit one final time to save any remaining changes
        if parser.check_verse_for_database_add():
            verse_obj = Verse(verse_num=parser.verse_num, text=parser.verse, chapter_id=parser.chapter.id)
            db.add(verse_obj)
            index_verse(verse_obj, parser.chapter, parser.subchapter)
        db.commit()
    finally:
        db.close()
