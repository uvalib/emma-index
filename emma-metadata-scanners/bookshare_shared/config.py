import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

BKS_CLIENT_ID = os.environ.get('BKS_API_KEY', 'Missing')
BKS_USERNAME = os.environ.get('BKS_API_USERNAME', 'Missing')
BKS_PASSWORD = os.environ.get('BKS_API_PASSWORD', 'Missing')
BKS_BASE_URL = os.environ.get('BKS_API_BASE_URL', 'https://api.qa.bookshare.org/v2')
BKS_TOKEN_URL = os.environ.get('BKS_API_TOKEN_URL', 'https://auth.qa.bookshare.org/oauth/token')
BKS_SITE = os.environ.get('BKS_SITE', 'bookshare')
BKS_RETRIEVALS = int(os.environ.get('BKS_RETRIEVALS', '10'))
BKS_PAGE_SIZE = int(os.environ.get('BKS_PAGE_SIZE', '20'))


BKS_API_KEY_PARAM = {'api_key': BKS_CLIENT_ID}

X_BOOKSHARE_ORIGIN = os.environ.get('X_BOOKSHARE_ORIGIN', 'Missing')
BKS_HEADERS = {'X-Bookshare-Origin': X_BOOKSHARE_ORIGIN}

EMMA_INGESTION_URL = os.environ.get('EMMA_INGESTION_URL', '{{REDACTED}}')
EMMA_API_KEY = os.environ.get('EMMA_API_KEY', '{{REDACTED}}')

EMMA_BATCH_LIMIT = 1000



