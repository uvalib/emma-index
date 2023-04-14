import json
import re
from pprint import pprint
import pytest
from jsonschema import Draft7Validator

from ingestion import put
from tests.shared import test_helpers


def test_lambda_empty_body(apigw_event):
    # Set up the data
    del apigw_event['body']
    # Run the test
    ret = put.lambda_handler(apigw_event, "")
    # Check the results
    assert ret['statusCode'] == 400
    errors = json.loads(ret['body'])
    assert errors['body'][0] == "Body is empty"


def test_lambda_invalid_json_body(apigw_event):
    # Set up the data
    apigw_event['body'] = test_helpers.get_invalid_json_body()
    # Run the test
    ret = put.lambda_handler(apigw_event, "")
    # Check the results
    assert ret['statusCode'] == 400
    errors = json.loads(ret['body'])
    assert errors['body'][0] == "Submitted data is not valid JSON"


def test_lambda_malformed_doc_body(apigw_event):
    # Set up the data
    apigw_event['body'] = test_helpers.get_malformed_json_body() 
    # Run the test
    ret = put.lambda_handler(apigw_event, "")
    # Check the results
    assert ret['statusCode'] == 400
    errors = json.loads(ret['body'])
    assert len(errors['document-1']) == 4


def test_lambda_too_many_records(apigw_event):
    # Set up the data
    apigw_event['body'] = test_helpers.get_too_many_records()
    # Run the test
    ret = put.lambda_handler(apigw_event, "")
    # Check the results
    assert ret['statusCode'] == 400
    errors = json.loads(ret['body'])
    assert errors['body'][0] == "Submitted data contains more than 1000 records"


def test_lambda_some_error_doc_body(apigw_event, requests_mock):
    # Set up the data
    elasticsearch_url_matcher = re.compile('.*_bulk.*')
    requests_mock.post(elasticsearch_url_matcher,
                       text=test_helpers.sample_elasticsearch_put_response())
    apigw_event['body'] = test_helpers.get_good_mixed_record_list()
    # Run the test
    ret = put.lambda_handler(apigw_event, "")
    # Check the results
    assert ret['statusCode'] == 207
    errors = json.loads(ret['body'])
    assert ('document-1' not in errors)
    assert ('document-2' in errors)
    assert ('document-3' not in errors)


def test_lambda_good_dates_doc_body(apigw_event, requests_mock):
    # Set up the data
    elasticsearch_url_matcher = re.compile('.*_bulk.*')
    requests_mock.post(elasticsearch_url_matcher,
                       text=test_helpers.sample_elasticsearch_put_response())
    apigw_event['body'] = test_helpers.get_json_body_good_dates()
    # Run the test
    ret = put.lambda_handler(apigw_event, "")

    # Check the results
    assert ret['statusCode'] == 202
    assert ret['body'] == ''


def test_lambda_bad_dates_doc_body(apigw_event, requests_mock):
    # Set up the data
    elasticsearch_url_matcher = re.compile('.*_bulk.*')
    requests_mock.post(elasticsearch_url_matcher,
                       text=test_helpers.sample_elasticsearch_put_response())
    apigw_event['body'] = test_helpers.get_json_body_bad_dates()
    # Run the test
    ret = put.lambda_handler(apigw_event, "")

    # Check the results
    assert ret['statusCode'] == 400
    errors = json.loads(ret['body'])
    assert ('document-1' in errors)


    assert any(msg.startswith('rem_remediationDate') for msg in errors['document-1'])
    assert any(msg.startswith('emma_sortDate') for msg in errors['document-1'])
    assert any(msg.startswith('emma_repositoryUpdateDate') for msg in errors['document-1'])
    assert any(msg.startswith('dcterms_dateAccepted') for msg in errors['document-1'])
    assert any(msg.startswith('emma_publicationDate') for msg in errors['document-1'])


def test_lambda_good_doc_body(apigw_event, requests_mock):
    # Set up the data
    elasticsearch_url_matcher = re.compile('.*_bulk.*')
    requests_mock.post(elasticsearch_url_matcher,
                       text=test_helpers.sample_elasticsearch_put_response())

    apigw_event['body'] = test_helpers.get_good_json_body()
    # Run the test
    ret = put.lambda_handler(apigw_event, "")
    # Check the results
    assert ret['statusCode'] == 202
    assert ret['body'] == ''


def test_lambda_bad_regex_patterns(apigw_event):
    # Set up the data
    apigw_event['body'] = test_helpers.get_bad_regex_pattern_body()
    # Run the test
    ret = put.lambda_handler(apigw_event, "")
    # Check the results
    errors = json.loads(ret['body'])
    for err in errors:
        assert any(msg.startswith('dc_identifier') for msg in errors[err])
        assert any(msg.startswith('dc_language') for msg in errors[err])
        assert any(msg.startswith('dcterms_dateCopyright') for msg in errors[err])


def test_lambda_good_regex_patterns(apigw_event, requests_mock):
    # Set up the data
    elasticsearch_url_matcher = re.compile('.*_bulk.*')
    requests_mock.post(elasticsearch_url_matcher,
                       text=test_helpers.sample_elasticsearch_put_response())
    apigw_event['body'] = test_helpers.get_good_regex_pattern_body()
    # Run the test
    ret = put.lambda_handler(apigw_event, "")
    # Check the results
    assert ret['body'] == ''
    assert ret['statusCode'] == 202


def test_json_validation():
    ''' 
    Test that the schema we are using correctly validates a reasonable ingestion record 
    '''
    # Set up the data
    with open('ingestion/ingestion-record.schema.json', 'r') as schema_file:
        data = schema_file.read()
    ingestion_schema = json.loads(data)
    with open('tests/unit/ingestion/examples/harry-potter-1-brf-grade1.json') as data_file:
        data = data_file.read()
    ingestion_record = json.loads(data)

    # Run the test
    Draft7Validator.check_schema(ingestion_schema)
    validator = Draft7Validator(ingestion_schema)

    # Check the results (throws exception on failure)
    validator.validate(ingestion_record)


def test_causes_502_hit(apigw_event, requests_mock):
    # Set up the data
    elasticsearch_url_matcher = re.compile('.*_bulk.*')
    requests_mock.post(elasticsearch_url_matcher,
                       text=test_helpers.sample_elasticsearch_put_response())
    elasticsearch_search_url_matcher = re.compile('.*_search.*')
    requests_mock.get(elasticsearch_search_url_matcher,
                      text=test_helpers.sample_title_hit_response())

    apigw_event['body'] = test_helpers.get_causes_dc_identifier_error()
    # Run the test
    ret = put.lambda_handler(apigw_event, "")
    # Check the results
    assert ret['statusCode'] == 202
    assert ret['body'] == ''


def test_causes_502_miss(apigw_event, requests_mock):
    # Set up the data
    elasticsearch_url_matcher = re.compile('.*_bulk.*')
    requests_mock.post(elasticsearch_url_matcher,
                       text=test_helpers.sample_elasticsearch_put_response())
    elasticsearch_search_url_matcher = re.compile('.*_search.*')
    requests_mock.get(elasticsearch_search_url_matcher,
                      text=test_helpers.sample_title_miss_response())

    apigw_event['body'] = test_helpers.get_causes_dc_identifier_error()
    # Run the test
    ret = put.lambda_handler(apigw_event, "")
    # Check the results
    assert ret['statusCode'] == 202
    assert ret['body'] == ''



# -------------- Test data functions

@pytest.fixture()
def apigw_event():
    """ Generates API GW Event"""

    return {
        "body": "{ \"test\": \"body\"}",
        "resource": "/{proxy+}",
        "requestContext": {
            "resourceId": "123456",
            "apiId": "1234567890",
            "resourcePath": "/{proxy+}",
            "httpMethod": "PUT",
            "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
            "accountId": "123456789012",
            "identity": {
                "apiKey": "",
                "userArn": "",
                "cognitoAuthenticationType": "",
                "caller": "",
                "userAgent": "Custom User Agent String",
                "user": "",
                "cognitoIdentityPoolId": "",
                "cognitoIdentityId": "",
                "cognitoAuthenticationProvider": "",
                "sourceIp": "127.0.0.1",
                "accountId": ""
            },
            "stage": "prod"
        },
        "headers": {
            "Via":
            "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
            "Accept-Language":
            "en-US,en;q=0.8",
            "CloudFront-Is-Desktop-Viewer":
            "true",
            "CloudFront-Is-SmartTV-Viewer":
            "false",
            "CloudFront-Is-Mobile-Viewer":
            "false",
            "X-Forwarded-For":
            "127.0.0.1, 127.0.0.2",
            "CloudFront-Viewer-Country":
            "US",
            "Accept":
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Upgrade-Insecure-Requests":
            "1",
            "X-Forwarded-Port":
            "443",
            "Host":
            "1234567890.execute-api.us-east-1.amazonaws.com",
            "X-Forwarded-Proto":
            "https",
            "X-Amz-Cf-Id":
            "aaaaaaaaaae3VYQb9jd-nvCd-de396Uhbp027Y2JvkCPNLmGJHqlaA==",
            "CloudFront-Is-Tablet-Viewer":
            "false",
            "Cache-Control":
            "max-age=0",
            "User-Agent":
            "Custom User Agent String",
            "CloudFront-Forwarded-Proto":
            "https",
            "Accept-Encoding":
            "gzip, deflate, sdch"
        },
        "pathParameters": {
            "proxy": "/examplepath"
        },
        "httpMethod": "PUT",
        "stageVariables": {
            "baz": "qux"
        },
        "path": "/examplepath"
    }
