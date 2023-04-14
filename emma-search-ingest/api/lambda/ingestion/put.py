'''
put.py
AWS Lambda function emma-federated-ingest-put
Upserts a list of records from the EMMA Federated Index
'''
import json
import os

import shared.config
from ingestion_validator.DocValidator import DocValidator
from ingestion_handler.UpsertHandler import UpsertHandler
from shared import helpers

# Look in lambda location, then in local location
INGESTION_SCHEMA_FILE = 'ingestion-record.schema.json' if os.path.exists('ingestion-record.schema.json') \
    else 'ingestion/ingestion-record.schema.json'

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

        if len(errors) == 0 and len(document_list) > 0:
            try:
                doc_validator = DocValidator(INGESTION_SCHEMA_FILE)
                upsert_handler = UpsertHandler(shared.config.EMMA_ELASTICSEARCH_INDEX, doc_validator)
                upsert_handler.submit(es, document_list, errors)
            except Exception as e:
                print(e)
                return {
                    "statusCode": 500,
                    "body": "Upsert handler exception " + str(e) + "\n" + str(json.dumps(document_list)) + "\n" + str(json.dumps(errors))
                }

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


