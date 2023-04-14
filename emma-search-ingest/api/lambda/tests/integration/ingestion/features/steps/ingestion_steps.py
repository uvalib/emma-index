import json
import requests
from behave import *

from shared.helpers import listify
from tests.integration import config
from tests.shared import test_helpers

emma_headers = {'x-api-key': config.EMMA_API_KEY}


@given('We create a metadata record')
def step_impl(context):
    body = test_helpers.get_good_integration_title()
    context.metadata_record = json.loads(body)
    context.params = {}


@given('We create a remediated metadata record')
def step_impl(context):
    body = test_helpers.get_remediated_integration_title()
    context.metadata_record = json.loads(body)
    context.params = {}


@given('We specify a metadata record')
def step_impl(context):
    context.record_id = 'bookshare-1-brf'
    body = test_helpers.get_good_integration_title()
    context.metadata_record = json.loads(body)
    context.params = {}


@given('We specify a remediated metadata record')
def step_impl(context):
    context.record_id = 'bookshare-2-brf'
    body = test_helpers.get_remediated_integration_title()
    context.metadata_record = json.loads(body)
    context.params = {}


@when('We submit the record')
def step_impl(context):
    context.response_obj = requests.put(config.INGESTION_URL,
                                        headers=emma_headers,
                                        json=context.metadata_record,
                                        params=context.params)


@when('We delete the record')
def step_impl(context):
    delete_request = [{"emma_recordId": context.record_id}]
    context.response_obj = requests.post(config.DELETE_URL,
                                         headers=emma_headers,
                                         json=delete_request,
                                         params=context.params)


@when('We request the record')
def step_impl(context):
    get_request = [{"emma_recordId": context.record_id}]
    context.response_obj = requests.post(config.GET_URL,
                                         headers=emma_headers,
                                         json=get_request,
                                         params=context.params)


@then('We get a successful ingestion code')
@then('We get a successful deletion code')
def step_impl(context):
    assert context.response_obj.status_code == 202


@then('We get the record metadata')
def step_impl(context):
    assert context.response_obj.status_code == 200
    response_json = context.response_obj.json()[0]
    original_json = context.metadata_record[0]
    for key in original_json:
        original = listify(original_json[key])
        response = listify(response_json[key])
        original = sorted(original)
        response = sorted(response)
        assert original == response

    print(json.dumps(context.response_obj.json(), indent=4))

