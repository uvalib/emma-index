import json
import re

import pytest

from tests.shared import test_helpers
from ingestion import recordDeletes


def test_lambda_some_error_doc_body(apigw_event, requests_mock):
    # Set up the data
    elasticsearch_url_matcher = re.compile('.*_bulk.*')
    requests_mock.post(elasticsearch_url_matcher,
                       text=sample_elasticsearch_delete_response())
    apigw_event['body'] = test_helpers.get_good_mixed_record_id_list()
    # Run the test
    ret = recordDeletes.lambda_handler(apigw_event, "")
    # Check the results
    assert ret['statusCode'] == 207
    errors = json.loads(ret['body'])
    assert ('document-1' not in errors)
    assert ('document-2' in errors)
    assert ('document-3' not in errors)


def test_lambda_good_doc_body_record_id(apigw_event, requests_mock):
    # Set up the data
    elasticsearch_url_matcher = re.compile('.*_bulk.*')
    requests_mock.post(elasticsearch_url_matcher,
                       text=sample_elasticsearch_delete_response())

    apigw_event['body'] = test_helpers.get_good_json_body_record_id()
    # Run the test
    ret = recordDeletes.lambda_handler(apigw_event, "")
    # Check the results
    assert ret['statusCode'] == 202
    assert ret['body'] == ''

def test_lambda_good_doc_body_composite_id(apigw_event, requests_mock):
    # Set up the data
    elasticsearch_url_matcher = re.compile('.*_bulk.*')
    requests_mock.post(elasticsearch_url_matcher,
                       text=sample_elasticsearch_delete_response())

    apigw_event['body'] = test_helpers.get_good_json_body_composite_id()
    # Run the test
    ret = recordDeletes.lambda_handler(apigw_event, "")
    # Check the results
    assert ret['statusCode'] == 202
    assert ret['body'] == ''


# -------------- Test data functions

def sample_elasticsearch_delete_response():
    return json.dumps(
        {
            "took": 10,
            "errors": False,
            "items": [
                {
                    "update": {
                        "_index": "emma-federated-index",
                        "_type": "_doc",
                        "_id": "bookshare-32480-brf",
                        "_version": 1,
                        "result": "created",
                        "_shards": {
                            "total": 2,
                            "successful": 1,
                            "failed": 0
                        },
                        "_seq_no": 4,
                        "_primary_term": 1,
                        "status": 201
                    }
                }
            ]
        }
    )


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
