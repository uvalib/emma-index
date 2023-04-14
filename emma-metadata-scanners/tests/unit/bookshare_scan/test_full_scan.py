"""
Test 'full scan' scenarios.  That is, test scenarios where there is no end boundary
set by a previous run.  These scenarios apply to the ginormous first run where all of Bookshare is read in.
Test that the correct number of records are processed and that the job status is accurately read from 
and updated to the Dynamo DB table.
"""
import logging
import re

import requests
from moto import mock_dynamodb2

from bookshare_scan import main
from bookshare_shared import config
from shared import dynamo, dynamo_config
from tests.unit.bookshare_scan import test_data
from tests.unit.bookshare_scan.test_data import PAGE_1_RECORD_3_ID, LAST_RECORD_ID
from tests.unit.shared import test_helpers

# URL pattern matchers for mocking requests
# No 'start' parameter
config.BKS_PAGE_SIZE = 3
config.BKS_RETRIEVALS = 3
bks_first_page_matcher = re.compile('^(?!.*start=).*')
bks_second_page_matcher_full = re.compile('.*limit=' + str(config.BKS_PAGE_SIZE) + '.*start=Page1Next.*')
bks_second_page_matcher_partial = re.compile('.*limit=' + str(config.BKS_PAGE_SIZE - 1) + '.*start=Page1Next.*')
bks_third_page_matcher = re.compile('.*start=Page2Next.*')
emma_ingest_matcher = re.compile('.*/records.*')


def setup_mock(requests_mock):
    # Return some fake Bookshare API V2 calls for 3 pages of results
    requests_mock.get(bks_first_page_matcher, text=test_data.get_page_1())
    requests_mock.get(bks_second_page_matcher_full, text=test_data.get_page_2())
    requests_mock.get(bks_second_page_matcher_partial, text=test_data.get_partial_page_2())
    requests_mock.get(bks_third_page_matcher, text=test_data.get_page_3())

    # Return one successful EMMA ingestion result
    requests_mock.put(emma_ingest_matcher, text="", status_code=202)



@mock_dynamodb2
def test_bookshare_full_scan(requests_mock):
    """
    Full scan with no start record, no boundary record
    """
    # Set up the data
    setup_mock(requests_mock)
    table = test_helpers.create_dynamo_table(dynamo_config.DYNAMODB_LOADER_TABLE)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)


    # Run the test
    main.run(requests, table, logger)

    # Check the results   
    assert dynamo.get_db_value(table, dynamo.SCAN_BATCH_COMPLETED) == True
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING) == False
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_ID) == LAST_RECORD_ID
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP) == '2019-12-08T16:00:00Z'
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING_TOTAL_SOURCE) == 6
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING_TOTAL_FEDERATED) == 29
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP) == '2019-12-09T23:00:00Z'
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP) is None


@mock_dynamodb2
def test_bad_param(requests_mock):
    """
    Test how the data loader reacts to a 400 error from the Bookshare API as if we've sent a bad parameter
    """
    # Set up the data
    setup_mock(requests_mock)
    requests_mock.get(bks_second_page_matcher_full, text=test_data.get_bks_bad_param_response(), status_code=400)

    table = test_helpers.create_dynamo_table(dynamo_config.DYNAMODB_LOADER_TABLE)
    logger = logging.getLogger()

    # Run the test
    main.run(requests, table, logger)

    # Check the results   
    assert dynamo.get_db_value(table, dynamo.SCAN_BATCH_COMPLETED) == False
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING) == False
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_ID) == PAGE_1_RECORD_3_ID
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP) == '2019-12-09T21:00:00Z'
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING_TOTAL_SOURCE) == 3
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING_TOTAL_FEDERATED) == 14
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP) is None
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP) == '2019-12-09T23:00:00Z'


@mock_dynamodb2
def test_bks_not_auth(requests_mock):
    """
    Simulate a situation where the next page (page 2 here) returns an unauthorized error.
    """
    # Set up the data
    setup_mock(requests_mock)
    requests_mock.get(bks_second_page_matcher_full, text=test_data.get_bks_unauthorized_response(), status_code=401)

    table = test_helpers.create_dynamo_table(dynamo_config.DYNAMODB_LOADER_TABLE)
    logger = logging.getLogger()

    # Run the test
    main.run(requests, table, logger)

    # Check the results   
    assert dynamo.get_db_value(table, dynamo.SCAN_BATCH_COMPLETED) == False
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING) == False
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_ID) == PAGE_1_RECORD_3_ID
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP) == '2019-12-09T21:00:00Z'
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING_TOTAL_SOURCE) == 3
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING_TOTAL_FEDERATED) == 14
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP) is None
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP) == '2019-12-09T23:00:00Z'


@mock_dynamodb2
def test_bks_bad_start(requests_mock):
    """
    Simulate a situation where the next token we send to the Bookshare API as the start parameter is garbage.
    """
    # Set up the data
    setup_mock(requests_mock)
    # When I tested, this also returned a 500 rather than 400 from the Bookshare API
    requests_mock.get(bks_second_page_matcher_full, text=test_data.get_bks_bad_start_param_response(), status_code=500)

    table = test_helpers.create_dynamo_table(dynamo_config.DYNAMODB_LOADER_TABLE)
    logger = logging.getLogger()

    # Run the test
    main.run(requests, table, logger)

    # Check the results
    assert dynamo.get_db_value(table, dynamo.SCAN_BATCH_COMPLETED) == False
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING) == False
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_ID) == PAGE_1_RECORD_3_ID
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP) == '2019-12-09T21:00:00Z'
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING_TOTAL_SOURCE) == 3
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING_TOTAL_FEDERATED) == 14
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP) is None
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP) == '2019-12-09T23:00:00Z'
