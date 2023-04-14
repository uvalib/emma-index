import os
import boto3
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection


ES_CONFIGS = {'dev': {'host': os.environ.get('ES_HOST_DEV', None), 'index': os.environ.get('ES_INDEX_DEV', None)},
              'qa': {'host': os.environ.get('ES_HOST_QA', None), 'index': os.environ.get('ES_INDEX_QA', None)},
              'staging': {'host': os.environ.get('ES_HOST_STAGING', None),
                          'index': os.environ.get('ES_INDEX_STAGING', None)}
              }

ES_REGION = 'us-east-1'
ES_SERVICE = 'es'



def init_connections():
    credentials = boto3.Session().get_credentials()
    aws_auth = AWS4Auth(credentials.access_key, credentials.secret_key,
                        ES_REGION, ES_SERVICE, session_token=credentials.token)
    for env in ES_CONFIGS.keys():
        env_config = ES_CONFIGS[env]
        env_config['conn'] = Elasticsearch(
            hosts=[{'host': env_config['host'], 'port': 443}],
            http_auth=aws_auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection)

init_connections()