import os
import boto3
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection

INGESTION_RECORD_LIMIT = 1000

DEFAULT_ELASTICSEARCH_HOST = 'vpc-{{REDACTED}}.es.amazonaws.com'
DEFAULT_ELASTICSEARCH_INDEX = 'emma-federated-index'

EMMA_ELASTICSEARCH_HOST = os.environ.get('EMMA_ELASTICSEARCH_HOST', DEFAULT_ELASTICSEARCH_HOST)
EMMA_ELASTICSEARCH_INDEX = os.environ.get('EMMA_ELASTICSEARCH_INDEX', DEFAULT_ELASTICSEARCH_INDEX)
EMMA_ELASTICSEARCH_REGION = 'us-east-1'
EMMA_ELASTICSEARCH_SERVICE = 'es'

GOLDEN_KEY = os.environ.get('GOLDEN_KEY', 'unset')

credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key,
                   EMMA_ELASTICSEARCH_REGION, EMMA_ELASTICSEARCH_SERVICE, session_token=credentials.token)

ELASTICSEARCH_CONN = Elasticsearch(
    hosts=[{'host': EMMA_ELASTICSEARCH_HOST, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

RENAMED_FIELDS = {
    'emma_lastRemediationNote':'rem_comments',
    'emma_lastRemediationDate': 'rem_remediationDate',
    'emma_repositoryMetadataUpdateDate': 'emma_repositoryUpdateDate'
}

ORIGINAL_FIELDS = {
    'rem_comments':'emma_lastRemediationNote',
    'rem_remediationDate': 'emma_lastRemediationDate',
    'emma_repositoryUpdateDate': 'emma_repositoryMetadataUpdateDate'
}