import os

GOLDEN_KEY = os.environ.get('GOLDEN_KEY', 'dev')
INGESTION_API_ID = os.environ.get('INGESTION_API_ID', 'unset')
SEARCH_API_ID = os.environ.get('SEARCH_API_ID', 'unset')
INGEST_API_KEY = os.environ.get('INGEST_API_KEY', '{{REDACTED}}')

DEFAULT_REGION = 'us-east-1'
AWS_PROFILE = os.environ.get('AWS_PROFILE', None)

EVENTBRIDGE_SCAN_FUNCTION_RULE_MAP = {
    'internet-archive-scan': 'scan-every-15-minutes',
    'bookshare-scan': 'scan-every-15-minutes',
    'hathitrust-get-file': 'scan-every-60-minutes'
}

SQS_SCAN_FUNCTION_MAP = {'hathitrust-scan': 'incoming-metadata-to-process'}

EMMA_PROFILE_ID_NUMBER = os.environ.get('PROFILE_ID', '')
LAMBDA_ARN_PREFIX = "arn:aws:lambda:" + DEFAULT_REGION + ":" + EMMA_PROFILE_ID_NUMBER + ":function:"
SQS_ARN_PREFIX = "arn:aws:sqs:" + DEFAULT_REGION + ":" + EMMA_PROFILE_ID_NUMBER + ":"
EVENTBRIDGE_RULE_ARN_PREFIX = "arn:aws:events:" + DEFAULT_REGION + ":" + EMMA_PROFILE_ID_NUMBER + ":rule/"
LAMBDA_INTEGRATION_PREFIX = "arn:aws:apigateway:" + DEFAULT_REGION + ":lambda:path/functions/"
LAMBDA_INTEGRATION_SUFFIX = "/invocations"
LAMBDA_EXECUTE_PERMISSION_PREFIX = "arn:aws:execute-api:" + DEFAULT_REGION + ":" + EMMA_PROFILE_ID_NUMBER


