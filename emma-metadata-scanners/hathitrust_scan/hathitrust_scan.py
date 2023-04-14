"""
hathitrust_scan.py
AWS Lambda function hathitrust-scan
Sends HathiTrust records to the EMMA Federated Index ingestion endpoint
"""
import logging
import boto3
import json

from hathitrust_scan import main

def lambda_handler(event, context):
    """
    Top-level function that handles the incoming lambda event
    """
    # We know the following has a table.
    # pylint: disable=maybe-no-member
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    print("Triggering event: " + json.dumps(event))

    s3_resource = boto3.resource('s3')

    # S3 event wrapped in SQS event
    records = json.loads(event['Records'][0]['body'])

    source_bucket = records['Records'][0]['s3']['bucket']['name']
    source_key = records['Records'][0]['s3']['object']['key']

    main.run(s3_resource, source_bucket, source_key, logger)





