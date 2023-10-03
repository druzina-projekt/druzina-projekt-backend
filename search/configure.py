import os

from elasticsearch import Elasticsearch
from .mappings import create_book_mapping, create_chapter_mapping, create_subchapter_mapping, create_verse_mapping

ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME")
ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD")
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST")
ELASTICSEARCH_PORT = os.getenv("ELASTICSEARCH_PORT")
ELASTICSEARCH_SCHEME = os.getenv("ELASTICSEARCH_SCHEME")

# WARNING: verify_certs needs to be set to true and correctly configured in a PRODUCTION enviroment
es = Elasticsearch(
    hosts=[{'host': ELASTICSEARCH_HOST, 'port': int(ELASTICSEARCH_PORT), 'scheme': ELASTICSEARCH_SCHEME}],
    http_auth=(ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD),
    verify_certs=False
)


def create_indices():
    # Define the mappings
    book_mapping = create_book_mapping()
    chapter_mapping = create_chapter_mapping()
    subchapter_mapping = create_subchapter_mapping()
    verse_mapping = create_verse_mapping()

    # Create the indices if they do not exist
    if not es.indices.exists(index='books'):
        es.indices.create(index='books', body={'mappings': book_mapping})

    if not es.indices.exists(index='chapters'):
        es.indices.create(index='chapters', body={'mappings': chapter_mapping})

    if not es.indices.exists(index='subchapters'):
        es.indices.create(index='subchapters', body={'mappings': subchapter_mapping})

    if not es.indices.exists(index='verses'):
        es.indices.create(index='verses', body={'mappings': verse_mapping})
