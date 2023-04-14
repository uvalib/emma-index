"""
recordGets.py
AWS Lambda function emma-federated-ingest-put
Gets a list of records from the EMMA Federated Index
"""
import json
import os

import boto3
from elasticsearch import RequestError

import shared.config
from jsonschema import Draft7Validator, ValidationError
from pprint import pprint
from shared import helpers
from ingestion_validator.DocValidator import DocValidator
from ingestion_handler.GetHandler import GetHandler

# Look in lambda location, then in local location
IDENTIFIER_SCHEMA_FILE = 'identifier-record.schema.json' if os.path.exists('identifier-record.schema.json') \
    else 'ingestion/identifier-record.schema.json'

es = shared.config.ELASTICSEARCH_CONN

def lambda_handler(event, context):
    """
    Top-level function that handles the incoming lambda event; a bulk get from ElasticSearch
    """

    errors = {}

    if 'body' in event and event['body']:
        body = event['body']

        # Check that body is valid JSON object
        document_list = helpers.get_json_list(body, errors)

        if len(errors) == 0:
            docValidator = DocValidator(IDENTIFIER_SCHEMA_FILE)
            getHandler = GetHandler(shared.config.EMMA_ELASTICSEARCH_INDEX, docValidator)
            statusCode = 200
            try:
                result = json.dumps(getHandler.submit(es, document_list, errors))
            except RequestError as e:
                errors['elasticsearch'] = [e.error]
        if len(errors) > 0 :
            # All documents rejected
            statusCode = 400
            result = json.dumps(errors)
    else:
        errors['body'] =['Body is empty']
        statusCode = 400
        result = json.dumps(errors)
    
    return {
        "statusCode": statusCode,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": result
    }






