from behave import *
from scanners.SqsManager import SqsManager
from shared.aws_util import fix_dates_aws_for_json
from tests.integration import config
import json
from time import sleep

from shared import config

@given('they are triggered by SQS events')
def step_impl(context):
    pass


@when('we disable the SQS triggers')
def step_impl(context):
    sqs_manager = SqsManager()
    response_list = sqs_manager.disable_ingest_sqs()
    context.response_list = response_list
    sleep(2)


@then('the SQS triggers are disabled')
def step_impl(context):
    assert_response_list_success(context.response_list)
    sqs_manager = SqsManager()
    sqs_manager.verify(False)


@when('we enable the SQS triggers')
def step_impl(context):
    sqs_manager = SqsManager()
    response_list = sqs_manager.enable_ingest_sqs()
    context.response_list = response_list
    sleep(2)


@then('the SQS triggers are enabled')
def step_impl(context):
    assert_response_list_success(context.response_list)
    sqs_manager = SqsManager()
    sqs_manager.verify(True)



def assert_response_list_success(response_list):
    for response in response_list:
        assert response['ResponseMetadata']['HTTPStatusCode'] == 202
