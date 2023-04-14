import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

IA_SECRET_KEY = os.environ.get('IA_SECRET_KEY', 'Missing')
IA_ACCESS_KEY = os.environ.get('IA_ACCESS_KEY', 'Missing')
IA_SITE = os.environ.get('IA_SITE', 'internetArchive')
IA_REPOSITORY_NAME = os.environ.get('IA_REPOSITORY_NAME','internetArchive')
IA_SESSION_CONFIG = {'s3': {'access': IA_ACCESS_KEY, 'secret': IA_SECRET_KEY}}
IA_SCRAPE_URL = 'https://archive.org/services/search/v1/scrape'
IA_PERSONALIZE = os.environ.get('IA_PERSONALIZE','')


IA_COLLECTION_LIST = os.environ.get('IA_COLLECTION_LIST', 'internetarchivebooks').split(",")
IA_FORMATS = os.environ.get('IA_FORMATS', 'PDF,(MARC Binary)').split(",")

EMMA_INGESTION_URL = os.environ.get('EMMA_INGESTION_URL', 'Missing')
EMMA_API_KEY = os.environ.get('EMMA_API_KEY', 'Missing')
EMMA_INGESTION_LIMIT = int(os.environ.get('EMMA_INGESTION_LIMIT', 100))
EMMA_INGESTION_RETRY = int(os.environ.get('EMMA_INGESTION_RETRY', 2))

# From the Internet Archive API:
# [RANGE_OUT_OF_BOUNDS] paging is only supported through 10000 results; scraping is supported through 
# the Scraping API, see https://archive.org/help/aboutsearch.htm  or, you may request up to 100000000 
# results at one time if you do NOT specify any page. For best results,  do NOT specify sort 
# (sort may be automatically disabled for very large queries).

IA_PAGE_SIZE = int(os.environ.get('IA_PAGE_SIZE', 100))
IA_RETRIEVALS = int(os.environ.get('IA_RETRIEVALS', 5))
DATE_BOUNDARY_FIELD = 'indexdate'

SEARCH_FIELDS = ['collection',
                 'creator',
                 'date',
                 'description',
                 'external-identifier',
                 'format',
                 'isbn',
                 'identifier',
                 'indexdate',
                 'language',
                 'lccn',
                 'licenseurl',
                 'mediatype',
                 'name',
                 'oclc',
                 'publisher',
                 'related-external-id',
                 'rights',
                 'subject',
                 'title',
                 'type',
                 'year'
                 ]

SEARCH_PARAMS = {'count': IA_PAGE_SIZE,
                 # Causes IA error: "userid xxxxxxx is not authorized to access .", errorType: "unknown"
                 # 'scope': 'all'
                 'fields' : ','.join(SEARCH_FIELDS),
                 'personalize': IA_PERSONALIZE}

HEADERS = {
    'Authorization': 'LOW '+IA_ACCESS_KEY+':'+IA_SECRET_KEY
}

'''
All the fields we know about
This is not incredibly well documented, so leaving it here for now.
SEARCH_FIELDS = ['addeddate',
                 'avg_rating',
                 'backup_location',
                 'btih',
                 'call_number',
                 'collection',
                 'contributor',
                 'coverage',
                 'creator',
                 'createdate',
                 'date',
                 'description',
                 'downloads',
                 'external-identifier',
                 'foldoutcount',
                 'format',
                 'genre',
                 'headerImage',
                 'isbn',
                 'identifier',
                 'imagecount',
                 'indexflag',
                 'indexdate',
                 'item_size',
                 'language',
                 'lccn',
                 'licenseurl',
                 'mediatype',
                 'members',
                 'month',
                 'name',
                 'noindex',
                 'num_reviews',
                 'oai_updatedate',
                 'oclc',
                 'publicdate',
                 'publisher',
                 'related-external-id',
                 'reviewdate',
                 'rights',
                 'scanningcentre',
                 'source',
                 'stripped_tags',
                 'subject',
                 'title',
                 'type',
                 'updatedate',
                 'volume',
                 'week',
                 'year'
                 ]
'''