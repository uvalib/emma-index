import json
import pytest
import re
from search import get
from pprint import pprint
from tests.shared import test_helpers


def test_retrieval_good(requests_mock):
    # Set up the data
    elasticsearch_url_matcher = re.compile('.*_search.*')
    requests_mock.get(elasticsearch_url_matcher,
                      text=sample_elasticsearch_response())

    queryStringParameters = {
        "q": "potter",
        "format": "brf",
        "formatFeature": "grade1",
        "formatVersion": "1.0",
        "accessibilityFeature": "bookmarks",
        "repository": "bookshare",
        "collection": "New York Times Bestsellers",
        "lastRemediationDate": "2012-01-01",
        "sort": "title",
        "size": "33",
        "searchAfterId": "100001t100003a",
        "searchAfterValue": "Harry%20Potter"
    }

    multiValueQueryStringParameters = {
        "formatFeature": ["grade1", "ueb"],
        "accessibilityFeature": ["bookmarks", "braille", "structuralNavigation"],
    }

    # Run the test
    query, errors = get.build_query_with_relevance(queryStringParameters, multiValueQueryStringParameters)

    # Validate the results
    assert len(errors) == 0
    filter_dicts = query.to_dict()['query']['bool']['filter']
    assert len(filter_dicts) == 7


    # Create simple list of strings
    # Validate filters that take single value
    filters = list(map(lambda f: list(f['term'].keys())[0]  if 'term' in f else 'other', filter_dicts))
    filterable_list = ['emma_formatVersion']
    # Make sure filter exists
    for filterable in filterable_list:
        result = [fil for fil in filters if filterable == fil]
        assert result

    # Validate filters that take multi value
    multi_filters = list(map(lambda f: list(f['terms'].keys())[0]  if 'terms' in f else 'other', filter_dicts))
    multi_filterable_list = ['dc_format', 'emma_formatFeature', 's_accessibilityFeature', 'emma_collection']

    # Make sure filter exists
    for filterable in multi_filterable_list:
        result = [fil for fil in multi_filters if filterable == fil]
        assert result


def test_q_query_creation():
    # Set up the data
    queryStringParameters = {
        "q": "something",
        "creator": "j.k. rowling",
        "title": "harry potter",
        "identifier": "123"
    }

    # Run the test
    query, errors = get.build_query_with_relevance(queryStringParameters, [])

    # Validate the results
    assert len(errors) == 0
    query_dict = query.to_dict()['query']
    assert query_dict.get('bool', None) is not None
    bool_dict = query_dict['bool']
    assert bool_dict.get('should', None) is not None
    should_list = bool_dict['should']
    assert should_list[0].get('multi_match', None) is not None
    multi_match_dict = should_list[0]['multi_match']
    assert multi_match_dict['query'] == 'something'
    assert multi_match_dict['fields'] is not None

def test_q_query_numeric_creation():
    # Set up the data
    queryStringParameters = {
        "q": "something a123"
    }

    # Run the test
    query, errors = get.build_query_with_relevance(queryStringParameters, [])

    # Validate the results
    assert len(errors) == 0
    query_dict = query.to_dict()['query']
    assert query_dict.get('bool', None) is not None
    bool_dict = query_dict['bool']
    assert bool_dict.get('should', None) is not None
    should_list = bool_dict['should']
    for multi_match_dict in should_list:
        if 'something' in multi_match_dict['multi_match']['query']:
            for text_field in multi_match_dict['multi_match']['fields']:
                assert 'numeric' not in text_field
        else:
            for potential_id_field in multi_match_dict['multi_match']['fields']:
                assert 'numeric' in potential_id_field


def test_individual_fields_query_creation():
    # Set up the data
    queryStringParameters = {
        "creator": "rowling",
        "title": "title",
        "identifier": "123",
        "publisher": "harlequin"
    }

    # Run the test
    query, errors = get.build_query_with_relevance(queryStringParameters, [])

    # Validate the results
    assert len(errors) == 0
    query_dict = query.to_dict()['query']
    assert query_dict.get('bool', None) is not None
    bool_dict = query_dict['bool']
    assert bool_dict['must'] is not None
    assert(len(bool_dict['must'])) == 4

    # q argument is thrown out
    assert query_dict.get('multi_match', None) is None


def test_lambda_handler(apigw_event, requests_mock):
    # Set up the data
    elasticsearch_url_matcher = re.compile('.*_search.*')
    requests_mock.get(elasticsearch_url_matcher,
                      text=sample_elasticsearch_response())

    apigw_event['queryStringParameters'] = {"q": "potter", "sort": "title"}

    # Run the test
    ret = get.lambda_handler(apigw_event, "")

    # Check the results
    assert ret['statusCode'] == 200
    assert ret['body'] == sample_emma_response()


def test_lambda_handler_no_arg(requests_mock):
    # Set up the data

    # Run the test
    ret = get.lambda_handler({}, "")

    # Check the results
    assert ret['statusCode'] == 400


def test_lambda_handler_bad_arg(apigw_event, requests_mock):
    # Set up the data
    elasticsearch_url_matcher = re.compile('.*_search.*')
    requests_mock.get(elasticsearch_url_matcher,
                      text=sample_elasticsearch_response())
    apigw_event['queryStringParameters'] = {"q": "potter", "format": "xxx"}

    # Run the test
    ret = get.lambda_handler(apigw_event, "")

    # Check the results
    assert ret['statusCode'] == 400
    assert ret['body'] == json.dumps(["format xxx not in accepted list brf, daisy, daisyAudio, epub, braille, pdf, grayscalePdf, word, tactile, kurzweil, rtf"])


def test_lambda_handler_too_many(apigw_event, requests_mock):
    # Set up the data
    elasticsearch_url_matcher = re.compile('.*_search.*')
    requests_mock.get(elasticsearch_url_matcher,
                      text=sample_elasticsearch_response())
    apigw_event['queryStringParameters'] = {"size": "100", "from": "950", "q": "potter"}

    # Run the test
    ret = get.lambda_handler(apigw_event, "")

    # Check the results
    assert ret['statusCode'] == 400
    assert ret['body'] == json.dumps(["Only up to 1000 records can be retrieved from a relevance query."])


def test_lambda_handler_bad_sort_from(apigw_event, requests_mock):
    # Set up the data
    elasticsearch_url_matcher = re.compile('.*_search.*')
    requests_mock.get(elasticsearch_url_matcher,
                      text=sample_elasticsearch_response())
    apigw_event['queryStringParameters'] = {"sort": "title", "from": "20", "q": "potter"}

    # Run the test
    ret = get.lambda_handler(apigw_event, "")

    # Check the results
    assert ret['statusCode'] == 400
    assert "The sort parameter cannot be used with the from parameter." in ret['body']


def test_lambda_handler_bad_search_after(apigw_event, requests_mock):
    # Set up the data
    elasticsearch_url_matcher = re.compile('.*_search.*')
    requests_mock.get(elasticsearch_url_matcher,
                      text=sample_elasticsearch_response())
    apigw_event['queryStringParameters'] = {"sort": "title", "searchAfterId": "20", "q": "potter"}

    # Run the test
    ret = get.lambda_handler(apigw_event, "")

    # Check the results
    assert ret['statusCode'] == 400
    assert ret['body'] == json.dumps(["searchAfterId and searchAfterValue parameters must either both be present or neither be present."])

def test_grouped_query_result(apigw_event, requests_mock):

    # Set up the data
    elasticsearch_url_matcher = re.compile('.*_search.*')
    requests_mock.get(elasticsearch_url_matcher,
                      text=test_helpers.get_sample_elasticsearch_groups_response())
    query_string_parameters = {
        "title": "the stand",
        "group": "emma_titleId"
    }
    apigw_event['queryStringParameters'] = query_string_parameters

    # Run the test
    ret = get.lambda_handler(apigw_event, "")

    # Check the results
    body = json.loads(ret['body'])
    for record in body:
        related = record["related_records"]
        record_ids = [rec["emma_recordId"] for rec in related]
        assert len(set(record_ids)) == len(related)


# Bogus Lambda event (gets fed to lambda handler event parameter)
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
            "q": "potter",
            "logquery": ""
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
                            "dc_language": ["eng"],
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
                            ],
                            "rem_comments": "New EPUB3 file",
                            "rem_remediationDate": "2018-05-17"
                        }
                    }
                ]
            }
        }
    )


# Bogus desired response from our web service
def sample_emma_response():
    return json.dumps(
        [
            {
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
                "dc_creator": ["J. K. Rowling"],
                "dc_identifier": ["isbn:9780439064873"],
                "dc_publisher": "Scholastic",
                "dc_language": ["eng"],
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
                "s_accessibilityFeature": ["braille"],
                "s_accessibilityControl": ["fullKeyboardControl"],
                "s_accessibilityHazard": [
                    "noFlashingHazard",
                    "noMotionSimulationHazard",
                    "noSoundHazard"
                ],
                "rem_comments": "New EPUB3 file",
                "rem_remediationDate": "2018-05-17"
            }
        ]
    )
