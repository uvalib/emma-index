"""
bring_online.py
Enable the ingestion and scanning processes
Necessary, for example, for snapshot and restore
"""

import json

from scanners.EventBridgeManager import EventBridgeManager
from scanners.SqsManager import SqsManager
from apigateway.ApiGatewayManager import ApiGatewayManager
from shared import config
from shared.aws_util import fix_dates_aws_for_json
from time import sleep

ENV = config.GOLDEN_KEY


def lambda_handler(event, context):
    """
    Top-level function that handles the call to the lambda function coming from AWS.
    """
    code = 200

    responses = []

    print("Beginning bringing " + ENV + " API services online")
    api_gateway_manager = ApiGatewayManager(ENV)
    response = api_gateway_manager.enable_ingest_api()
    responses.extend(response)
    print(json.dumps(fix_dates_aws_for_json(response), sort_keys=True, indent=4))
    sleep(60)
    api_gateway_manager.verify(True)

    sqs_manager = SqsManager(ENV)
    response = sqs_manager.enable_ingest_sqs()
    responses.extend(response)
    print(json.dumps(fix_dates_aws_for_json(response), sort_keys=True, indent=4))
    sqs_manager.verify(True)

    event_manager = EventBridgeManager(ENV, config.AWS_PROFILE)
    response = event_manager.enable_ingest_eventbridge()
    responses.extend(response)
    print(json.dumps(fix_dates_aws_for_json(response), sort_keys=True, indent=4))
    event_manager.verify(True)

    print("Completed bringing " + ENV + " API services online")

    body = {'responses': responses}

    body_json = json.dumps(body, sort_keys=True, indent=4)

    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": body_json
    }

