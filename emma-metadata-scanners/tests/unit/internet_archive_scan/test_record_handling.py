"""
Test that the record handling functions can find and iterate
through records
"""

from internetarchive import get_session
from moto import mock_dynamodb2
from unittest.mock import ANY, Mock, patch, call
from http.client import HTTPMessage

import logging
import json

from internet_archive_shared import config, record_handling
from shared import dynamo
from shared import dynamo_config
from tests.unit.internet_archive_scan import test_data
from tests.unit.shared import test_helpers
from tests.unit.shared.test_helpers import print_dynamo_value

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@mock_dynamodb2
def test_get_next_scrape_response(requests_mock):
    # Set up the data
    test_data.setup_mock(requests_mock)
    table = test_helpers.create_dynamo_table(dynamo_config.DYNAMODB_LOADER_TABLE)
    ia_session = get_session(config=config.IA_SESSION_CONFIG)

    # Run the test
    ia_response = record_handling.get_next_scrape_response(table)
    recs = record_handling.null_safe_get_items(ia_response.json())

    # Check the results
    assert len(recs) == 100
    for record in recs:
        assert len(record['collection']) > 0
        assert len(record['identifier']) > 0
        assert len(record['format']) > 0
        assert len(record['title']) > 0


@mock_dynamodb2
def test_get_transform_send_page_1(requests_mock):
    # Set up the data
    test_data.setup_mock(requests_mock)
    ia_session = get_session(config=config.IA_SESSION_CONFIG)
    table = test_helpers.create_dynamo_table(dynamo_config.DYNAMODB_LOADER_TABLE)

    # Run the test
    num_records = record_handling.get_transform_send(ia_session, table)
    next_query = record_handling.build_query(table)

    # Check the results
    next_page = dynamo.get_db_value(table, dynamo.SCAN_NEXT_TOKEN)

    assert dynamo.get_db_value(table, dynamo.SCAN_BATCH_COMPLETED) is None
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING) is None
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_ID) == '12thinternationa0000inte'
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP) == '2019-08-06T17:15:59Z'
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING_TOTAL_SOURCE) == 100
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING_TOTAL_FEDERATED) == 300
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP) is None
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP) is None
    assert next_page == 'GET_PAGE_2_TOKEN'
    assert num_records == 300

@mock_dynamodb2
def test_get_transform_send_page_2(requests_mock):
    # Set up the data
    test_data.setup_mock(requests_mock)
    ia_session = get_session(config=config.IA_SESSION_CONFIG)
    table = test_helpers.create_dynamo_table(dynamo_config.DYNAMODB_LOADER_TABLE)
    dynamo.set_db_value(table, dynamo.SCAN_NEXT_TOKEN, 'GET_PAGE_2_TOKEN')
    dynamo.set_db_value(table, dynamo.SCAN_BATCH_COMPLETED, False)

    # Run the test
    num_records = record_handling.get_transform_send(ia_session, table)
    next_query = record_handling.build_query(table)

    # Check the results
    next_page = dynamo.get_db_value(table, dynamo.SCAN_NEXT_TOKEN)
    print(next_query)
    assert next_page == 'GET_PAGE_3_TOKEN'
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_ID) == '1975fortiethanni0000hous'
    assert num_records == 300


def test_batch_ingestion_failure(requests_mock):
    # Set up the data
    test_data.setup_mock_failure(requests_mock)
    with open('tests/unit/examples/emma_records_for_ingestion.json') as data_file:
        data = json.load(data_file)
    #Run test    
    record_handling.batch_to_ingestion(data)
    assert(requests_mock.call_count == 3)

def test_batch_ingestion_partial_failure(requests_mock):
    # Set up the data
    test_data.setup_mock_partial_failure(requests_mock)
    with open('tests/unit/examples/emma_records_for_ingestion.json') as data_file:
        data = json.load(data_file)
    #Run test    
    record_handling.batch_to_ingestion(data)
    assert(requests_mock.call_count == 3)

def test_batch_ingestion(requests_mock):
    # Set up the data
    test_data.setup_mock_ingestion(requests_mock)
    with open('tests/unit/examples/emma_records_for_ingestion.json') as data_file:
        data = json.load(data_file)
    #Run test    
    record_handling.batch_to_ingestion(data)
    assert(requests_mock.call_count == 3)

@patch("urllib3.connectionpool.HTTPConnectionPool._get_conn")
def test_retry_logic_sucess(getconn_mock):
    #Setup data
    getconn_mock.return_value.getresponse.side_effect = [
        Mock(status=429, msg=HTTPMessage()),
        Mock(status=429, msg=HTTPMessage()),
        Mock(status=202, msg=HTTPMessage()),
        Mock(status=202, msg=HTTPMessage()),
        Mock(status=429, msg=HTTPMessage()),
        Mock(status=429, msg=HTTPMessage()),
        Mock(status=202, msg=HTTPMessage())]
    with open('tests/unit/examples/emma_records_for_ingestion.json') as data_file:
        data = json.load(data_file)

    #Run test    
    record_handling.batch_to_ingestion(data)

    #Verify results
    assert len(getconn_mock.return_value.request.mock_calls)== 7

@patch("urllib3.connectionpool.HTTPConnectionPool._get_conn")
def test_retry_logic_failure(getconn_mock):
    #Setup data
    getconn_mock.return_value.getresponse.side_effect = [
        Mock(status=429, msg=HTTPMessage()),
        Mock(status=429, msg=HTTPMessage()),
        Mock(status=429, msg=HTTPMessage()),
        Mock(status=503, msg=HTTPMessage()),
        Mock(status=503, msg=HTTPMessage()),
        Mock(status=503, msg=HTTPMessage()),
        Mock(status=503, msg=HTTPMessage()),
        Mock(status=503, msg=HTTPMessage()),
        Mock(status=503, msg=HTTPMessage())]
    with open('tests/unit/examples/emma_records_for_ingestion.json') as data_file:
        data = json.load(data_file)

    #Run test    
    record_handling.batch_to_ingestion(data)

    #Verify results
    assert len(getconn_mock.return_value.request.mock_calls)== 9
@patch("urllib3.connectionpool.HTTPConnectionPool._get_conn")
def test_retry_logic_failure_nonretry_code(getconn_mock):
    #Setup data
    getconn_mock.return_value.getresponse.side_effect = [
        Mock(status=500, msg=HTTPMessage()),
        Mock(status=500, msg=HTTPMessage()),
        Mock(status=500, msg=HTTPMessage())]
    with open('tests/unit/examples/emma_records_for_ingestion.json') as data_file:
        data = json.load(data_file)

    #Run test    
    record_handling.batch_to_ingestion(data)

    #Verify results
    assert len(getconn_mock.return_value.request.mock_calls)== 3
 
