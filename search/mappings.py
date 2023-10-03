def create_book_mapping():
    return {
        'properties': {
            'book_num': {'type': 'integer'},
            'title': {'type': 'text'},
        }
    }


def create_chapter_mapping():
    return {
        'properties': {
            'chapter_num': {'type': 'integer'},
            'book_id': {'type': 'integer'},
        }
    }


def create_subchapter_mapping():
    return {
        'properties': {
            'title': {'type': 'text'},
        }
    }


def create_verse_mapping():
    return {
        'properties': {
            'verse_num': {'type': 'integer'},
            'text': {'type': 'text'},
            'chapter_id': {'type': 'integer'},
            'subchapter_id': {'type': 'integer'},
        }
    }
