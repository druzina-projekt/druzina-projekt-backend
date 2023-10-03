from logger import log
from .configure import es


def delete_all_documents():
    indices_to_delete = ['books', 'chapters', 'subchapters', 'verses']
    for index_name in indices_to_delete:
        log.info(f"Deleting all documents from index: {index_name}")
        es.delete_by_query(index=index_name, body={"query": {"match_all": {}}})
