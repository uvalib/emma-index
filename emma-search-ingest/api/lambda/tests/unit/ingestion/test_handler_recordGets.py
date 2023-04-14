import json
import re

import pytest

from ingestion import recordGets
from tests.shared import test_helpers


def test_lambda_some_error_doc_body(apigw_event, requests_mock):
    # Set up the data
    elasticsearch_url_matcher = re.compile('.*_mget.*')
    requests_mock.get(elasticsearch_url_matcher,
                       text=sample_elasticsearch_get_response())
    apigw_event['body'] = test_helpers.get_good_mixed_record_id_list()
    # Run the test
    ret = recordGets.lambda_handler(apigw_event, "")
    # Check the results

    assert ret['statusCode'] == 400
    errors = json.loads(ret['body'])
    assert ('document-1' not in errors)
    assert ('document-2' in errors)
    assert ('document-3' not in errors)


def test_lambda_good_doc_body_record_id(apigw_event, requests_mock):
    # Set up the data
    elasticsearch_url_matcher = re.compile('.*_mget.*')
    requests_mock.get(elasticsearch_url_matcher,
                       text=sample_elasticsearch_get_response())

    apigw_event['body'] = test_helpers.get_good_json_body_record_id()
    # Run the test
    ret = recordGets.lambda_handler(apigw_event, "")
    # Check the results
    assert ret['statusCode'] == 200
    body = json.loads(ret['body'])
    assert len(body) == 2


def test_lambda_good_doc_body_composite_id(apigw_event, requests_mock):
    # Set up the data
    elasticsearch_url_matcher = re.compile('.*_mget.*')
    requests_mock.get(elasticsearch_url_matcher,
                       text=sample_elasticsearch_get_response())

    apigw_event['body'] = test_helpers.get_good_json_body_composite_id()
    # Run the test
    ret = recordGets.lambda_handler(apigw_event, "")
    # Check the results
    assert ret['statusCode'] == 200
    body = json.loads(ret['body'])
    assert len(body) == 2


# -------------- Test data functions





def sample_elasticsearch_get_response():
    return json.dumps(
        {
            "docs": [
                {
                    "_index": "emma-federated-index",
                    "_type": "_doc",
                    "_id": "hathiTrust-100000-brf",
                    "_version": 2,
                    "_seq_no": 11,
                    "_primary_term": 1,
                    "found": True,
                    "_source": {
                        "emma_recordId": "hathiTrust-100000-brf",
                        "emma_titleId": "100000",
                        "emma_repository": "hathiTrust",
                        "emma_repositoryRecordId": "100000",
                        "emma_retrievalLink": "https://www.bookshare.org/browse/book/32480",
                        "emma_lastRemediationDate": "2019-01-01",
                        "emma_lastRemediationNote": "New EPUB3 file",
                        "emma_formatFeature": [
                           "grade1",
                           "ueb"
                        ],
                        "dc_title": "Harry Potter and the Sorcerer's Stone (Harry Potter #1)",
                        "dc_creator": "J. K. Rowling",
                        "dc_identifier": "isbn:9780590353427",
                        "dc_publisher": "Scholastic",
                        "dc_language": ["eng"],
                        "dc_rights": "copyright",
                        "dc_description": "Harry Potter has no idea how famous he is. That's because he's being raised by his miserable aunt and uncle who are terrified Harry will learn that he's really a wizard, just as his parents were. But everything changes when Harry is summoned to attend an infamous school for wizards, and he begins to discover some clues about his illustrious birthright. From the surprising way he is greeted by a lovable giant, to the unique curriculum and colorful faculty at his unusual school, Harry finds himself drawn deep inside a mystical world he never knew existed and closer to his own noble destiny.",
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
                },
                {
                    "_index": "emma-federated-index",
                    "_type": "_doc",
                    "_id": "bookshare-32480-daisy-3",
                    "_version": 1,
                    "_seq_no": 14,
                    "_primary_term": 1,
                    "found": True,
                    "_source": {
                        "emma_recordId": "bookshare-32480-daisy-3",
                        "emma_titleId": "100000",
                        "emma_repository": "bookshare",
                        "emma_repositoryRecordId": "32480",
                        "emma_retrievalLink": "https://www.bookshare.org/browse/book/32480",
                        "emma_lastRemediationDate": "2019-04-04",
                        "emma_lastRemediationNote": "New EPUB3 file",
                        "emma_formatVersion": "3",
                        "dc_title": "Harry Potter and the Sorcerer's Stone (Harry Potter #1)",
                        "dc_creator": "J. K. Rowling",
                        "dc_identifier": "isbn:9780590353427",
                        "dc_publisher": "Scholastic",
                        "dc_language": ["eng"],
                        "dc_rights": "copyright",
                        "dc_description": "Harry Potter has no idea how famous he is. That's because he's being raised by his miserable aunt and uncle who are terrified Harry will learn that he's really a wizard, just as his parents were. But everything changes when Harry is summoned to attend an infamous school for wizards, and he begins to discover some clues about his illustrious birthright. From the surprising way he is greeted by a lovable giant, to the unique curriculum and colorful faculty at his unusual school, Harry finds himself drawn deep inside a mystical world he never knew existed and closer to his own noble destiny.",
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
                        "dc_format": "daisy",
                        "dc_type": "text",
                        "dcterms_dateAccepted": "2015-11-13",
                        "dcterms_dateCopyright": "1997",
                        "s_accessibilityFeature": "alternativeText",
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
