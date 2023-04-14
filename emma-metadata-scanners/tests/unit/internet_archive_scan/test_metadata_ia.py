from internetarchive import get_session

from moto import mock_dynamodb2
from unittest import mock

from internet_archive_shared import config, metadata, record_handling
from shared import dynamo_config
from tests.unit.internet_archive_scan import test_data
from tests.unit.shared import test_helpers

import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@mock_dynamodb2
def test_transform(requests_mock):
    """
    Test that metadata records are appropriately transformed from
    Internet Archive API results format to EMMA Ingestion format
    """
    # Set up the data
    test_data.setup_mock(requests_mock)
    ia_records = get_search_results()

    ia_session = get_session(config=config.IA_SESSION_CONFIG)


    # Run the test
    transformed_records = metadata.transform_records(ia_records, ia_session)

    # Check the results
    assert len(transformed_records) == 300
    for sample_record in transformed_records:
        assert len(sample_record['dc_title']) > 0
        assert len(sample_record['dc_format']) > 0
        assert len(sample_record['emma_repository']) > 0
        assert len(sample_record['emma_repositoryRecordId']) > 0
        assert len(sample_record['emma_retrievalLink']) > 0
        for identifier in sample_record['dc_identifier']:
            assert identifier.find(r'[^0-9A-Za-z]') == -1

@mock_dynamodb2
def get_search_results():
    """
    We need results structured as they would be from the Python requests library,
    so we will go through this rigamarole of retrieving the results of a
    call to Internet Archive..
    """
    table = test_helpers.create_dynamo_table(dynamo_config.DYNAMODB_LOADER_TABLE)
    ia_response =  record_handling.get_next_scrape_response(table)
    return record_handling.null_safe_get_items(ia_response.json())


@mock_dynamodb2
def test_build_query():
    """
    We need results structured as they would be from the Python requests library,
    so we will go through this rigamarole of retrieving the results of a
    call to Internet Archive..
    """
    table = test_helpers.create_dynamo_table(dynamo_config.DYNAMODB_LOADER_TABLE)
    query =  record_handling.build_query(table)
    print(query)
    assert query == '_exists_:indexdate AND collection:(internetarchivebooks) AND mediatype:(texts) AND format:(PDF AND (MARC Binary))'
