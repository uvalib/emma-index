"""
take_offline.py
Disable the ingestion and scanning processes
Necessary, for example, for snapshot and restore
"""

import json

from scanners.EventBridgeManager import EventBridgeManager
from scanners.SqsManager import SqsManager
from apigateway.ApiGatewayManager import ApiGatewayManager
from shared import config
from shared.aws_util import fix_dates_aws_for_json, get_sts_client
from time import sleep

ENV = config.GOLDEN_KEY


def lambda_handler(event, context):
    """
    Top-level function that handles the call to the lambda function coming from AWS.
    """
    code = 200
    responses = []

    print("Beginning taking down " + ENV + " API services")

    client = get_sts_client()
    response = client.get_caller_identity()
    print(json.dumps(fix_dates_aws_for_json(response), sort_keys=True, indent=4))


    print("Disable " + ENV + " Eventbridge rules")
    event_manager = EventBridgeManager(ENV, config.AWS_PROFILE)
    response = event_manager.disable_ingest_eventbridge()
    responses.extend(response)
    print(json.dumps(fix_dates_aws_for_json(response), sort_keys=True, indent=4))

    print("Disable " + ENV + " SQS trigger")
    sqs_manager = SqsManager(ENV)
    response = sqs_manager.disable_ingest_sqs()
    responses.extend(response)
    print(json.dumps(fix_dates_aws_for_json(response), sort_keys=True, indent=4))

    print("Set " + ENV + " API gateway to maintenance message")

    api_gateway_manager = ApiGatewayManager(ENV)
    response = api_gateway_manager.disable_ingest_api()
    responses.extend(response)
    print(json.dumps(fix_dates_aws_for_json(response), sort_keys=True, indent=4))
    sleep(60)
    api_gateway_manager.verify(False)
    body = {'responses': responses}

    body_json = json.dumps(body, sort_keys=True, indent=4)
    print("Completed taking down " + ENV + " API services")

    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": body_json
    }

