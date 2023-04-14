from search_validator.Validator import Validator
from pprint import pprint;

def test_validation_good():
    # Set up the data
    query_string_parameters = {
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

    multi_value_query_string_parameters = {
        "formatFeature": ["grade1", "ueb"],
        "accessibilityFeature": ["bookmarks", "braille", "structuralNavigation"],
    }

    # Run the test
    errors = []

    # Run the test
    validator = Validator(query_string_parameters, multi_value_query_string_parameters)
    validator.validate(errors)

    assert not errors

def test_validation_bad():
    # Set up the data

    query_string_parameters = {
        "q": "potter",
        "format": "aaa",
        "formatFeature": "bbb",
        "formatVersion": "1.0",
        "accessibilityFeature": "ddd",
        "repository": "ggg",
        "collection": "New York Times Bestsellers",
        "lastRemediationDate": "hhh",
        "sort": "iii",
        "publicationDate" : "jjj"
    }

    multi_value_query_string_parameters = {
        "formatFeature": ["bbb", "ccc"],
        "accessibilityFeature": ["ddd", "eee", "fff"],
    }

    errors = []

    # Run the test
    validator = Validator(query_string_parameters, multi_value_query_string_parameters)
    validator.validate(errors)

    # Validate the results
    bad_values = ["aaa", "bbb", "ccc", "ddd", "eee", "fff", "ggg", "hhh", "iii", "jjj"]
    # Make sure error exists for bad value
    for bad_value in bad_values:
        result = [err for err in errors if bad_value in err]
        assert result
    assert len(errors) == 10


