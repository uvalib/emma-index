import boto3
import json
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch_dsl import Search
import requests
from requests_aws4auth import AWS4Auth

region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key,
                   region, service, session_token=credentials.token)

# For example, search-mydomain-id.us-west-1.es.amazonaws.com
host = 'vpc-{{REDACTED}}.es.amazonaws.com'
index = 'emma-federated-index-qa'
url = 'https://' + host + '/' + index + '/_search'

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# Lambda execution starts here

def lambda_handler(event, context):

    s = Search(using=es, index=index).query("match", dc_title="potter") \
        .filter("term", dc_format="brf")

    es_response = s.execute()

    # Create the response 
    response = {
        "statusCode": 200,
        "isBase64Encoded": False
    }

    # Add the search results to the response
    # Add the search results to the response
    transformed_results = []

    for hit in es_response.to_dict()['hits']['hits']:
            record = listify_record(hit['_source'])
            transformed_results.append(record)

    response['body'] = json.dumps(transformed_results)
    return response

def listify_record(record):
    """Make sure that properties that are defined as lists are returned as lists, even if there is only one value 
    in the list.
    """
    list_types = ['emma_formatFeature', 's_accessibilityControl', 's_accessibilityFeature',
                  's_accessibilityHazard', 's_accessibilityAPI', 's_accessMode', 's_accessModeSufficient', 'dc_subject',
                  'dc_relation', 'dc_identifier', 'dc_creator']
    for list_type in list_types:
        if list_type in record: 
            record[list_type] = listify(record[list_type])
    return record

def listify(prop):
    """If a single property is not  a list but should be, convert to a single-element list
    """
    return prop if isinstance(prop, list) else [prop] 
