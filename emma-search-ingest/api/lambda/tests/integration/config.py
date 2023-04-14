import logging
import http.client as http_client
import os


SEARCH_API_URL_FORMAT = 'https://api.{env}.bookshareunifiedsearch.org/search'
INGESTION_URL_FORMAT = 'https://ingest.{env}.bookshareunifiedsearch.org/records'
DELETE_URL_FORMAT = 'https://ingest.{env}.bookshareunifiedsearch.org/recordDeletes'
GET_URL_FORMAT = 'https://ingest.{env}.bookshareunifiedsearch.org/recordGets'

SEARCH_API_URL = "unset"
INGESTION_URL = "unset"
DELETE_URL = "unset"
GET_URL = "unset"

def set_servers(env):
    global SEARCH_API_URL
    global INGESTION_URL
    global DELETE_URL
    global GET_URL
    if not env:
        env = 'qa'

    SEARCH_API_URL = SEARCH_API_URL_FORMAT.format(env=env)
    INGESTION_URL = INGESTION_URL_FORMAT.format(env=env)
    DELETE_URL = DELETE_URL_FORMAT.format(env=env)
    GET_URL = GET_URL_FORMAT.format(env=env)

    if env == 'prod':
        SEARCH_API_URL = SEARCH_API_URL.replace('.prod', '')
        INGESTION_URL = INGESTION_URL.replace('.prod', '')
        DELETE_URL = DELETE_URL.replace('.prod', '')
        GET_URL = GET_URL.replace('.prod', '')


EMMA_API_KEY = os.environ.get('EMMA_API_KEY', 'none')

http_client.HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


