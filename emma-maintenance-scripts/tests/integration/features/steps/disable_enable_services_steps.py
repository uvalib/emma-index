from behave import *
from lambda_functions import take_offline, bring_online


@given('we have an ingestion API gateway, and scanners feeding into that gateway')
def step_impl(context):
    pass


@when('we disable the ingestion services')
def step_impl(context):
    take_offline.lambda_handler(None, None)


@when('we enable the ingestion services')
def step_impl(context):
    bring_online.lambda_handler(None, None)


@then('the services are disabled')
def step_impl(context):
    pass


@then('the services are enabled')
def step_impl(context):
    pass

