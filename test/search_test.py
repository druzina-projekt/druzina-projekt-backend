import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()

ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME")
ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD")
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST")
ELASTICSEARCH_PORT = os.getenv("ELASTICSEARCH_PORT")
ELASTICSEARCH_SCHEME = os.getenv("ELASTICSEARCH_SCHEME")

# WARNING: verify_certs needs to be set to true and correctly configured in a PRODUCTION enviroment
es = Elasticsearch(
    hosts=[{'host': ELASTICSEARCH_HOST, 'port': int(ELASTICSEARCH_PORT), 'scheme': ELASTICSEARCH_SCHEME}],
    basic_auth=(ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD),
    verify_certs=False
)

response = es.search(index="verses", query={
    "match_all": {}
})

for hit in response["hits"]["hits"]:
    print(hit["_source"])
