from behave import *
from scanners import SqsManager
from tests.integration import config
import json

from shared import config


@then('the request is successful')
def step_impl(context):
    status_code = context.response_obj['ResponseMetadata']['HTTPStatusCode']
    assert status_code == 200 or status_code == 202


