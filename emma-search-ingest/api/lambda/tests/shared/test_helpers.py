import json


def wrap_records(records_as_string):
    return '[' + records_as_string + ']'


def get_causes_upsert_502():
    with open('tests/unit/ingestion/examples/causes_502.json') as data_file:
        return data_file.read()


def get_causes_dc_identifier_error():
    with open('tests/unit/ingestion/examples/dc_identifier_error.json') as data_file:
        return data_file.read()


def get_malformed_json_body():
    with open('tests/unit/ingestion/examples/malformed-harry-potter-1-brf-id.json') as data_file:
        data = data_file.read()
        return wrap_records(data)


def get_good_json_body_composite_id():
    with open('tests/unit/ingestion/examples/harry-potter-1-brf-id.json') as data_file:
        data = data_file.read()
        return wrap_records(data)


def get_json_body_good_dates():
    with open('tests/unit/ingestion/examples/harry-potter-1-brf-grade1-good-dates.json') as data_file:
        data = data_file.read()
        return data


def get_json_body_bad_dates():
    with open('tests/unit/ingestion/examples/harry-potter-1-brf-grade1-bad-dates.json') as data_file:
        data = data_file.read()
        return wrap_records(data)


def get_good_json_body_record_id():
    with open('tests/unit/ingestion/examples/harry-potter-1-brf-alt-id.json') as data_file:
        data = data_file.read()
        return wrap_records(data)


def get_good_mixed_record_id_list():
    with open('tests/unit/ingestion/examples/harry-potter-1-brf-id.json') as data_file1:
        good = data_file1.read()
    with open('tests/unit/ingestion/examples/malformed-harry-potter-1-brf-id.json') as data_file2:
        bad = data_file2.read()
    list_data = good + "," + bad + "," + good
    return wrap_records(list_data)


def get_good_mixed_record_list():
    with open('tests/unit/ingestion/examples/harry-potter-1-brf-grade1.json') as data_file1:
        good = data_file1.read()
    with open('tests/unit/ingestion/examples/malformed-harry-potter-1-brf-grade1.json') as data_file2:
        bad = data_file2.read()
    list_data = good + "," + bad + "," + good
    return wrap_records(list_data)


def get_good_json_body():
    with open('tests/unit/ingestion/examples/harry-potter-1-brf-grade1.json') as data_file:
        data = data_file.read()
        return wrap_records(data)


def get_good_regex_pattern_body():
    with open('tests/unit/ingestion/examples/harry-potter-1-brf-grade1-test-good-regex.json') as data_file:
        data = data_file.read()
        return data


def get_bad_regex_pattern_body():
    with open('tests/unit/ingestion/examples/harry-potter-1-brf-grade1-test-bad-regex.json') as data_file:
        data = data_file.read()
        return data


def get_too_many_records():
    with open('tests/unit/ingestion/examples/harry-potter-1-brf-grade1.json') as data_file:
        data = data_file.read()
        too_many = ",".join(1001 * [data])
        return wrap_records(too_many)


def get_invalid_json_body():
    return "Just some garbage data."


def get_good_integration_title():
    with open('tests/integration/ingestion/examples/integration-test-valid-book-metadata.json') as data_file:
        data = data_file.read()
        return wrap_records(data)


def get_remediated_integration_title():
    with open('tests/integration/ingestion/examples/integration-test-valid-book-metadata-remediation-fields.json') as data_file:
        data = data_file.read()
        return wrap_records(data)


def get_json_not_a_list():
    return "{'records': 'Is not a list'}"


# Bogus sample ElasticSearch query result
def sample_title_hit_response():
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
                            ]
                        }
                    }
                ]
            }
        }
    )


def sample_title_miss_response():
    return json.dumps(
        {
            "took": 41,
            "timed_out": False,
            "_shards": {
                "total": 5,
                "successful": 5,
                "skipped": 0,
                "failed": 0
            },
            "hits": {
                "total": {
                    "value": 0,
                    "relation": "eq"
                },
                "max_score": None,
                "hits": []
            }
        }
    )


def sample_elasticsearch_put_response():
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


def get_sample_elasticsearch_groups_response() :
    """
    Results are grouped by emma_titleId
    """
    with open('tests/unit/search/examples/es_grouping_result.json') as data_file:
        return data_file.read()
