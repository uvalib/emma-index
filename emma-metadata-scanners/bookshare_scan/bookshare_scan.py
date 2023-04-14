"""
bookshare_scan.py
AWS Lambda function bookshare-upload-full-scan
Sends Bookshare records to the EMMA Federated Index ingestion endpoint
"""
import logging

import boto3

from bookshare_scan import main
from bookshare_shared import oauth_conn
from shared import dynamo_config


def lambda_handler(event, context):
    """
    Top-level function that handles the incoming lambda event
    """
    dynamodb = boto3.resource('dynamodb')
    # We know the following has a table.
    # pylint: disable=maybe-no-member
    table = dynamodb.Table(dynamo_config.DYNAMODB_LOADER_TABLE)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    oauth_session = oauth_conn.oauth
    main.run(oauth_session, table, logger)





