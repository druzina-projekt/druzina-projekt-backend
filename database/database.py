import os

from sqlalchemy import create_engine, MetaData
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, declarative_base

from logger import log

Base = declarative_base()

POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE")

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    log.info("Initializing database...")

    # Import models to create
    from models import Book, Chapter, Subchapter, Verse
    log.info(f"Models imported: {Book}, {Chapter}, {Subchapter}, {Verse}")

    # Create tables
    Base.metadata.create_all(bind=engine, tables=[Book.__table__, Chapter.__table__, Subchapter.__table__, Verse.__table__])
    log.info("Tables created.")

    # WARNING: only for development purposes (deletes all data from the database)
    truncate_db_data()


def truncate_db_data():
    metadata = MetaData()
    metadata.reflect(bind=engine)

    with engine.connect() as conn:
        try:
            for table in reversed(metadata.sorted_tables):
                log.info(f"Deleting data from table: {table.name}")
                conn.execute(table.delete())
            conn.commit()
        except SQLAlchemyError as e:
            log.error(f"An error occurred while deleting data: {e}")
            conn.rollback()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
