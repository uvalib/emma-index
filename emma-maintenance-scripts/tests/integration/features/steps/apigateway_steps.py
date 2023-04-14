from behave import *
from apigateway.ApiGatewayManager import ApiGatewayManager
from time import sleep



@given('we have an ingestion API gateway')
def step_impl(context):
    pass


@when('we disable the API gateway')
def step_impl(context):
    api_gateway_manager = ApiGatewayManager()
    context.response_obj = api_gateway_manager.disable_ingest_api()
    sleep(1)


@when('we enable the API gateway')
def step_impl(context):
    api_gateway_manager = ApiGatewayManager()
    context.response_obj = api_gateway_manager.enable_ingest_api()
    sleep(1)


@then('the API gateway is disabled')
def step_impl(context):
    sleep(15)
    api_gateway_manager = ApiGatewayManager()
    context.response_obj = api_gateway_manager.verify(False)


@then('the API gateway is enabled')
def step_impl(context):
    sleep(15)
    api_gateway_manager = ApiGatewayManager()
    context.response_obj = api_gateway_manager.verify(True)
