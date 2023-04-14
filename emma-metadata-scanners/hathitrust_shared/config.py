import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

EMMA_INGESTION_URL = os.environ.get('EMMA_INGESTION_URL', 'Missing')

EMMA_API_KEY = os.environ.get('EMMA_API_KEY', 'Missing')

SQS_URL = os.environ.get('SQS_URL', 'Missing')
SOURCE_BUCKET = os.environ.get('SOURCE_BUCKET', 'Missing')

BKS_RECORD_LIST_SIZE = 100

