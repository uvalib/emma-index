from behave import *
from shared.helpers import exists
import requests
from tests.integration import config
import pprint

PARAM_TO_FIELD_MAP = {
    "title": "dc_title",
    "publisher": "dc_publisher",
    "creator": "dc_creator",
    "format": "dc_format"
}

@given('We quick search for "{q}"')
def step_impl(context, q):
    context.params = {'q': q, 'logquery': 'yes'}


@given('We search on individual parameters')
def step_impl(context):
    context.params = {'logquery': 'yes'}


@given('{param_name} as "{param_value}"')
def step_impl(context, param_name, param_value):
    context.params[param_name] = param_value


@given('we sort by {param_value}')
def step_impl(context, param_value):
    context.params['sort'] = param_value


@when('we retrieve {pages:d} pages')
def step_impl(context, pages):
    params = context.params
    multipage_data = []
    result_codes = []
    for i in range(pages):
        context.response_obj = requests.get(config.SEARCH_API_URL, params=params)
        data = context.response_obj.json()
        multipage_data.extend(data)
        result_codes.append(context.response_obj.status_code)
        search_after_field = get_internal_sort_field(params)
        if data is None or len(data) < 1:
            break
        if isinstance(data[-1], dict) and exists(data[-1], search_after_field):
            params['searchAfterValue'] = data[-1][search_after_field]
            params['searchAfterId'] = data[-1]['emma_recordId']
    context.data = multipage_data
    context.result_codes = result_codes


@when('we retrieve {pages:d} relevance sorted pages')
def step_impl(context, pages):
    params = context.params
    multipage_data = []
    result_codes = []
    from_param = 0
    size_param = get_size(context)
    for i in range(pages):
        context.response_obj = requests.get(config.SEARCH_API_URL, params=params)
        data = context.response_obj.json()
        for j in range(len(data) - 1):
            if exists(data[j], "dc_title"):
                print(data[j]["dc_title"])
        multipage_data.extend(data)
        result_codes.append(context.response_obj.status_code)
        if data is None or len(data) < 1:
            break
        from_param = from_param + size_param
        params['from'] = from_param
    context.data = multipage_data
    context.result_codes = result_codes


@when('we execute the search')
def step_impl(context):
    context.response_obj = requests.get(config.SEARCH_API_URL, params=context.params)
    print(str(context.response_obj.text))
    context.data = context.response_obj.json()
    print(str(context.response_obj.status_code))


@then('we get a success code')
def step_impl(context):
    assert context.response_obj.status_code == 200


@then('we get success codes')
def step_impl(context):
    all(context.result_codes[i] == 200 for i in range(len(context.result_codes) - 1))


@then('the last page has bad request code')
def step_impl(context):
    assert(context.result_codes[-1] == 400)


@then('the last page has message "{message}"')
def step_impl(context, message):
    assert(context.data[-1] == (message))


@then('results are sorted in {param_name} order')
def step_impl(context, param_name):
    data = context.response_obj.json()
    assert_data_sorted(context, data)


@then('pages are sorted in {param_name} order')
def step_impl(context, param_name):
    page_data = context.data
    assert_data_sorted(context, page_data)


@then('the first {num_results:d} results contain "{param_value}" in the {param_name}')
def step_impl(context, num_results, param_value, param_name):
    data = context.response_obj.json()
    field = PARAM_TO_FIELD_MAP[param_name]
    print(data[0][field].lower())
    print(param_value.lower())
    for i in range(num_results):
        assert param_value.lower() in data[i][field].lower()


def assert_data_sorted(context, data):
    internal_sort_field_name = get_internal_sort_field(context.params)
    all(not exists(data[i], internal_sort_field_name)
        or not exists(data[i + 1], internal_sort_field_name)
        or data[i][internal_sort_field_name] <= data[i + 1][internal_sort_field_name] for i in
        range(len(data) - 1))
    print("Length: " + str(len(data)))
    for i in range(len(data) - 1):
        if exists(data[i], internal_sort_field_name):
            print(data[i][internal_sort_field_name])
        else:
            print(internal_sort_field_name + " is None")
    assert context.response_obj.status_code == 200


def get_internal_sort_field(params):
    field_name = 'dc_title'
    if exists(params, "sort"):
        sort = params["sort"]
        if sort == 'sortDate':
            field_name = 'emma_sortDate'
        if sort == 'lastRemediationDate':
            field_name = 'emma_lastRemediationDate'
        if sort == 'publicationDate':
            field_name = 'emma_publicationDate'
    return field_name


def get_size(context):
    size = 10
    if exists(context.params, "size"):
        size = int(context.params["size"])
    return size
