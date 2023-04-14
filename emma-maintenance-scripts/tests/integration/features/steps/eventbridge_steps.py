from behave import *
from scanners.EventBridgeManager import EventBridgeManager
from time import sleep


@given('we have scanner AWS Lambda functions')
def step_impl(context):
    pass


@given('they are running on a timed schedule')
def step_impl(context):
    pass


@when('we disable the timed triggers')
def step_impl(context):
    event_bridge_manager = EventBridgeManager()
    response_list = event_bridge_manager.disable_ingest_eventbridge()
    context.response_list = response_list
    sleep(1)


@then('the timed triggers are disabled')
def step_impl(context):
    assert_response_list_success(context.response_list)
    event_bridge_manager = EventBridgeManager()
    event_bridge_manager.verify(False)


@when('we enable the timed triggers')
def step_impl(context):
    event_bridge_manager = EventBridgeManager()
    response_list = event_bridge_manager.enable_ingest_eventbridge()
    context.response_list = response_list
    sleep(1)


@when('we grant permission for the timer to trigger those scanners')
def step_impl(context):
    pass
    # response_list = eventbridge.enable_ingest_eventbridge()
    # context.response_list = response_list


@then('the timed triggers are enabled')
def step_impl(context):
    assert_response_list_success(context.response_list)
    event_bridge_manager = EventBridgeManager()
    event_bridge_manager.verify(True)


@then('the permission is granted')
def step_impl(context):
    pass


def assert_response_list_success(response_list):
    for response in response_list:
        assert response['FailedEntryCount'] == 0
        assert response['ResponseMetadata']['HTTPStatusCode'] == 200
