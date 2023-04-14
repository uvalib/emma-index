import os

STATUS_TABLE_PREFIX = os.environ.get('EMMA_STATUS_TABLE_PREFIX', '')
DYNAMODB_LOADER_TABLE = os.environ.get('EMMA_STATUS_TABLE_NAME', 'emma_bookshare_loader')