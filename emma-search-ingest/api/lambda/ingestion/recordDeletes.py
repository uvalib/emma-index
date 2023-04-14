'''
put.py
AWS Lambda function emma-federated-ingest-put
Upserts, gets, or deletes a list of records from the EMMA Federated Index
'''
import json
import os

import boto3
import shared.config
from jsonschema import Draft7Validator, ValidationError
from pprint import pprint
from ingestion_validator.DocValidator import DocValidator
from ingestion_handler.DeleteHandler import DeleteHandler
from shared import helpers

# Look in lambda location, then in local location
IDENTIFIER_SCHEMA_FILE = 'identifier-record.schema.json' if os.path.exists('identifier-record.schema.json') \
    else 'ingestion/identifier-record.schema.json'

es = shared.config.ELASTICSEARCH_CONN

def lambda_handler(event, context):
    """
    Top-level function that handles the incoming lambda event; a bulk upsert to ElasticSearch
    """

    errors = {}
    result = {}

    if 'body' in event and event['body']:
        body = event['body']

        # Check that body is valid JSON object
        document_list = helpers.get_json_list(body, errors)

        if len(errors) == 0:
            docValidator = DocValidator(IDENTIFIER_SCHEMA_FILE)
            deleteHandler = DeleteHandler(shared.config.EMMA_ELASTICSEARCH_INDEX, docValidator)
            result = deleteHandler.submit(es, document_list, errors)

            if len(errors) == 0:
                # Good submission
                    statusCode = 202
            else:
                if len(errors) < len(document_list):
                    # Some documents rejected
                    statusCode = 207
                else:
                    # All documents rejected
                    statusCode = 400
        else:
            # All documents rejected
            statusCode = 400
    else:
        errors['body'] =['Body is empty']
        statusCode = 400

    body = helpers.string_or_nothing(result, errors)
    
    return {
        "statusCode": statusCode,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": body
    }



