"""
internet_archive_scan.py
AWS Lambda function internet-archive-scan
Sends Internet Archive records to the EMMA Federated Index ingestion endpoint
"""
import logging

import boto3
from internetarchive import get_session

from internet_archive_scan import main
from internet_archive_shared import config
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
    
    ia_session = get_session(config=config.IA_SESSION_CONFIG)
    main.run(ia_session, table, logger)





