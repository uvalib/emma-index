import json
import pytest
import re
from search_function import get_espy


def test_lambda_handler(apigw_event, requests_mock):
    # Set up the data
    elasticsearch_url_matcher = re.compile('.*_search.*')
    requests_mock.get(elasticsearch_url_matcher,
                      text=sample_elasticsearch_response())

    # Run the test
    ret = get_espy.lambda_handler(apigw_event, "")

    # Check the results
    assert ret['statusCode'] == 200


# This contains a lot of sample data sent by a typical API Gateway request
# to the lambda function.
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
            "httpMethod": "POST",
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
        "queryStringParameters": {
            "q": "potter"
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
        "httpMethod": "POST",
        "stageVariables": {
            "baz": "qux"
        },
        "path": "/examplepath"
    }


# Bogus sample ElasticSearch query result
def sample_elasticsearch_response():
    return json.dumps(
        {
            "took": 29,
            "timed_out": False,
            "_shards": {
                "total": 5,
                "successful": 5,
                "skipped": 0,
                "failed": 0
            },
            "hits": {
                "total": 1,
                "max_score": 1.0,
                "hits": [
                    {
                        "_index": "emma-federated-index",
                        "_type": "_doc",
                        "_id": "100001t100003a",
                        "_score": 1.0,
                        "_source": {
                            "emma_recordId": "100001t100003a",
                            "emma_titleId": "100001",
                            "emma_repository": "Bookshare",
                            "emma_repositoryRecordId": "24372",
                            "emma_retrievalLink": "https://www.bookshare.org/browse/book/24372",
                            "emma_lastRemediationDate": "2018-05-17",
                            "emma_lastRemediationNote": "New EPUB3 file",
                            "emma_formatFeature": [
                                "grade2",
                                "ueb"
                            ],
                            "dc_title": "Harry Potter and the Chamber of Secrets (Harry Potter #2)",
                            "dc_creator": "J. K. Rowling",
                            "dc_identifier": "isbn:9780439064873",
                            "dc_publisher": "Scholastic",
                            "dc_language": "en",
                            "dc_rights": "copyright",
                            "dc_description": "Book #2 in the Harry Potter phenomenon.",
                            "dc_subject": [
                                "bisac:JUV000000 JUVENILE FICTION / General",
                                "bisac:JUV037000 JUVENILE FICTION / Fantasy & Magic",
                                "bisac:JUV030050 JUVENILE FICTION / People & Places / Europe",
                                "bisac:JUV035000 JUVENILE FICTION / School & Education",
                                "bookshare:Education",
                                "bookshare:Science Fiction and Fantasy",
                                "bookshare:Literature and Fiction",
                                "bookshare:Children's Books",
                                "bookshare:Teens"
                            ],
                            "dc_format": "brf",
                            "dc_type": "text",
                            "dcterms_dateAccepted": "2015-11-13",
                            "dcterms_dateCopyright": "1997",
                            "s_accessibilityFeature": "braille",
                            "s_accessibilityControl": "fullKeyboardControl",
                            "s_accessibilityHazard": [
                                "noFlashingHazard",
                                "noMotionSimulationHazard",
                                "noSoundHazard"
                            ]
                        }
                    }
                ]
            }
        }
    )


# Bogus desired response from our web service
def sample_emma_response():
    return json.dumps(
        [{"title": "Harry Potter and the Chamber of Secrets (Harry Potter #2)",
          "author": "J. K. Rowling", "identifier": "isbn:9780439064873"}]
    )
