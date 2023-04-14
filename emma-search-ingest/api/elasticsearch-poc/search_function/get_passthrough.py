import boto3
import json
import requests
from requests_aws4auth import AWS4Auth
import os

"""
Passthrough ElasticSearch queries
"""

region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key,
                   region, service, session_token=credentials.token)

# For example, search-mydomain-id.us-west-1.es.amazonaws.com
DEFAULT_ELASTICSEARCH_HOST = 'vpc-{{REDACTED}}.es.amazonaws.com'
DEFAULT_ELASTICSEARCH_INDEX = 'emma-federated-index-qa'
DEFAULT_ELASTICSEARCH_TYPE = "search"

EMMA_ELASTICSEARCH_HOST = os.environ.get('EMMA_ELASTICSEARCH_HOST', DEFAULT_ELASTICSEARCH_HOST)
EMMA_ELASTICSEARCH_INDEX = os.environ.get('EMMA_ELASTICSEARCH_INDEX', DEFAULT_ELASTICSEARCH_INDEX)
EMMA_ELASTICSEARCH_TYPE = os.environ.get('EMMA_ELASTICSEARCH_TYPE', DEFAULT_ELASTICSEARCH_TYPE)
url = 'https://' + EMMA_ELASTICSEARCH_HOST + '/' + EMMA_ELASTICSEARCH_INDEX + '/_' + EMMA_ELASTICSEARCH_TYPE

# Lambda execution starts here
def lambda_handler(event, context):

    params = None
    if event and 'queryStringParameters' in event and isinstance(event['queryStringParameters'], dict) :
        params = event['queryStringParameters']
        print("Params\n")
        print(json.dumps(params))

    # ES 6.x requires an explicit Content-Type header
    headers = { "Content-Type": "application/json" }

    print('Calling: ' + url + '\n')

    # Make the signed HTTP request
    if params:
        r = requests.get(url, auth=awsauth, headers=headers, params=params)
    else:
        r = requests.get(url, auth=awsauth, headers=headers)

    # Create the response and add some extra content to support CORS
    response = {
        "statusCode": 200,
        "isBase64Encoded": False
    }

    response['body'] = r.text
    return response

