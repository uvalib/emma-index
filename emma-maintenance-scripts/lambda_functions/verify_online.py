"""
verify_online.py
Make sure ingestion and search are online
"""

import json

from scanners.EventBridgeManager import EventBridgeManager
from scanners.SqsManager import SqsManager
from apigateway.ApiGatewayManager import ApiGatewayManager
from shared import config

ENV = config.GOLDEN_KEY

def lambda_handler(event, context):
    """
    Top-level function that handles the call to the lambda function coming from AWS.
    Underlying methods throw assertion errors if any services are not online.
    """

    print("Verifying " + ENV + " API services online")
    api_gateway_manager = ApiGatewayManager(ENV)
    api_gateway_manager.verify(True)

    sqs_manager = SqsManager(ENV)
    sqs_manager.verify(True)

    event_manager = EventBridgeManager(ENV, config.AWS_PROFILE)
    event_manager.verify(True)

    print("Verified " + ENV + " API services online")



