"""
These tests check that the DynamoDB database returns to a valid state after each function call.
"""
import logging
from unittest.mock import patch

from moto import mock_dynamodb2
from tests.unit.shared import test_helpers
from bookshare_shared import config, record_handling
from bookshare_scan import main

from shared import dynamo, dynamo_config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Sample dates from an ordered timeline.

LAST_UPDATED_RECORD_TIMESTAMP_1 = '2001-01-01T00:00:00Z'
LAST_UPDATED_RECORD_TIMESTAMP_2 = '2002-01-01T00:00:00Z'
LAST_UPDATED_RECORD_TIMESTAMP_3 = '2003-01-01T00:00:00Z'
LAST_UPDATED_RECORD_TIMESTAMP_4 = '2004-01-01T00:00:00Z'
LAST_UPDATED_RECORD_TIMESTAMP_5 = '2005-01-01T00:00:00Z'
LAST_UPDATED_RECORD_TIMESTAMP_6 = '2006-01-01T00:00:00Z'
LAST_UPDATED_RECORD_TIMESTAMP_7 = '2006-01-01T00:00:00Z'

BATCH_BOUNDARY_TIMESTAMP_1 = '2001-01-02T00:00:00Z'
BATCH_BOUNDARY_TIMESTAMP_2 = '2002-01-02T00:00:00Z'
BATCH_BOUNDARY_TIMESTAMP_3 = '2003-01-02T00:00:00Z'
BATCH_BOUNDARY_TIMESTAMP_4 = '2004-01-02T00:00:00Z'
BATCH_BOUNDARY_TIMESTAMP_5 = '2005-01-02T00:00:00Z'
BATCH_BOUNDARY_TIMESTAMP_6 = '2006-01-02T00:00:00Z'
BATCH_BOUNDARY_TIMESTAMP_7 = '2007-01-02T00:00:00Z'


#--- Top level function calls

@mock_dynamodb2
@patch('bookshare_shared.record_handling.get_bookshare_page')
@patch('bookshare_shared.record_handling.get_first_record')
@patch('bookshare_shared.record_handling.is_batch_complete')
@patch('bookshare_shared.record_handling.send_records')
def test_start_first_batch(mock_send_records, mock_is_batch_complete, mock_get_first_record, mock_get_bookshare_page,
                              requests_mock):
    """
    Start fresh batch with no DB history
    """
    # Set up the data
    table = test_helpers.create_dynamo_table(dynamo_config.DYNAMODB_LOADER_TABLE)

    print('Before:')
    dump_dynamo(table)
    mock_get_first_record.return_value = {'lastUpdated': BATCH_BOUNDARY_TIMESTAMP_4}
    mock_is_batch_complete.return_value = False
    mock_get_bookshare_page.return_value = {
        'titles': [{'lastUpdated': LAST_UPDATED_RECORD_TIMESTAMP_4, 'bookshareId': 4}]}
    mock_send_records.return_value = True

    # Run the test
    main.run(requests_mock, table, logger)

    # Check the results
    print('After:')
    dump_dynamo(table)

    assert dynamo.get_db_value(table, dynamo.SCAN_BATCH_COMPLETED) == False
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING) == False
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_ID) == 4
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP) == LAST_UPDATED_RECORD_TIMESTAMP_4
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP) is None
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP) == BATCH_BOUNDARY_TIMESTAMP_4


@mock_dynamodb2
@patch('bookshare_shared.record_handling.get_bookshare_page')
@patch('bookshare_shared.record_handling.is_batch_complete')
@patch('bookshare_shared.record_handling.send_records')
def test_mid_batch(mock_send_records, mock_is_batch_complete, mock_get_bookshare_page,
                              requests_mock):
    """
    After one run has ended, pick up next run in same batch
    """
    # Set up the data

    table = test_helpers.create_dynamo_table(dynamo_config.DYNAMODB_LOADER_TABLE)

    # State at end of a batch
    dynamo.set_db_value(table, dynamo.SCAN_BATCH_COMPLETED, False)
    dynamo.set_db_value(table, dynamo.SCAN_RUNNING, False)
    dynamo.set_db_value(table, dynamo.LAST_UPDATED_RECORD_ID, 4)
    dynamo.set_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP, LAST_UPDATED_RECORD_TIMESTAMP_4)
    dynamo.set_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP, BATCH_BOUNDARY_TIMESTAMP_4)
    print('Before:')
    dump_dynamo(table)
    mock_is_batch_complete.return_value = False
    mock_get_bookshare_page.return_value = {
        'titles': [{'lastUpdated': LAST_UPDATED_RECORD_TIMESTAMP_3, 'bookshareId': 3}]}
    mock_send_records.return_value = True

    # Run the test
    main.run(requests_mock, table, logger)

    # Check the results
    print('After:')
    dump_dynamo(table)

    assert dynamo.get_db_value(table, dynamo.SCAN_BATCH_COMPLETED) == False
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING) == False
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_ID) == 3
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP) == LAST_UPDATED_RECORD_TIMESTAMP_3
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP) is None
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP) == BATCH_BOUNDARY_TIMESTAMP_4

@mock_dynamodb2
@patch('bookshare_shared.record_handling.get_bookshare_page')
@patch('bookshare_shared.record_handling.is_batch_complete')
@patch('bookshare_shared.record_handling.send_records')
def test_end_batch(mock_send_records, mock_is_batch_complete, mock_get_bookshare_page,
                              requests_mock):
    """
    Close out a batch
    """
    # Set up the data

    table = test_helpers.create_dynamo_table(dynamo_config.DYNAMODB_LOADER_TABLE)

    # State at end of a batch
    dynamo.set_db_value(table, dynamo.SCAN_BATCH_COMPLETED, False)
    dynamo.set_db_value(table, dynamo.SCAN_RUNNING, False)
    dynamo.set_db_value(table, dynamo.LAST_UPDATED_RECORD_ID, 3)
    dynamo.set_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP, LAST_UPDATED_RECORD_TIMESTAMP_3)
    dynamo.set_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP, BATCH_BOUNDARY_TIMESTAMP_4)
    print('Before:')
    dump_dynamo(table)
    mock_is_batch_complete.return_value = True
    mock_get_bookshare_page.return_value = {
        'titles': [{'lastUpdated': LAST_UPDATED_RECORD_TIMESTAMP_2, 'bookshareId': 2}]}
    mock_send_records.return_value = True

    # Run the test
    main.run(requests_mock, table, logger)

    # Check the results
    print('After:')
    dump_dynamo(table)

    assert dynamo.get_db_value(table, dynamo.SCAN_BATCH_COMPLETED) == True
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING) == False
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_ID) == 2
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP) == LAST_UPDATED_RECORD_TIMESTAMP_2
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP) == BATCH_BOUNDARY_TIMESTAMP_4
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP) is None

@mock_dynamodb2
@patch('bookshare_shared.record_handling.get_bookshare_page')
@patch('bookshare_shared.record_handling.get_first_record')
@patch('bookshare_shared.record_handling.is_batch_complete')
@patch('bookshare_shared.record_handling.send_records')
def test_start_diff_batch(mock_send_records, mock_is_batch_complete, mock_get_first_record, mock_get_bookshare_page,
                              requests_mock):
    """
    After one batch has ended, start a new batch (with history in DB)
    """
    # Set up the data

    table = test_helpers.create_dynamo_table(dynamo_config.DYNAMODB_LOADER_TABLE)

    # State at end of last batch
    dynamo.set_db_value(table, dynamo.SCAN_BATCH_COMPLETED, True)
    dynamo.set_db_value(table, dynamo.SCAN_RUNNING, False)
    dynamo.set_db_value(table, dynamo.LAST_UPDATED_RECORD_ID, 2)
    dynamo.set_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP, LAST_UPDATED_RECORD_TIMESTAMP_2)
    dynamo.set_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP, BATCH_BOUNDARY_TIMESTAMP_4)
    print('Before:')
    dump_dynamo(table)
    mock_get_first_record.return_value = {'lastUpdated': BATCH_BOUNDARY_TIMESTAMP_7}
    mock_is_batch_complete.return_value = False
    mock_get_bookshare_page.return_value = {
        'titles': [{'lastUpdated': LAST_UPDATED_RECORD_TIMESTAMP_7, 'bookshareId': 7}]}
    mock_send_records.return_value = True

    # Run the test
    main.run(requests_mock, table, logger)

    # Check the results
    print('After:')
    dump_dynamo(table)

    assert dynamo.get_db_value(table, dynamo.SCAN_BATCH_COMPLETED) == False
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING) == False
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_ID) == 7
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP) == LAST_UPDATED_RECORD_TIMESTAMP_7
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP) == BATCH_BOUNDARY_TIMESTAMP_4
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP) == BATCH_BOUNDARY_TIMESTAMP_7


@mock_dynamodb2
@patch('bookshare_shared.record_handling.get_bookshare_page')
@patch('bookshare_shared.record_handling.is_batch_complete')
@patch('bookshare_shared.record_handling.send_records')
def test_mid_diff_batch(mock_send_records, mock_is_batch_complete, mock_get_bookshare_page,
                              requests_mock):
    """
    After one batch has ended, start a new batch (with history in DB)
    """
    # Set up the data

    table = test_helpers.create_dynamo_table(dynamo_config.DYNAMODB_LOADER_TABLE)

    # State at end of last batch
    dynamo.set_db_value(table, dynamo.SCAN_BATCH_COMPLETED, False)
    dynamo.set_db_value(table, dynamo.SCAN_RUNNING, False)
    dynamo.set_db_value(table, dynamo.LAST_UPDATED_RECORD_ID, 7)
    dynamo.set_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP, LAST_UPDATED_RECORD_TIMESTAMP_7)
    dynamo.set_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP, BATCH_BOUNDARY_TIMESTAMP_4)
    dynamo.set_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP, BATCH_BOUNDARY_TIMESTAMP_7)

    print('Before:')
    dump_dynamo(table)
    mock_is_batch_complete.return_value = False
    mock_get_bookshare_page.return_value = {
        'titles': [{'lastUpdated': LAST_UPDATED_RECORD_TIMESTAMP_6, 'bookshareId': 6}]}
    mock_send_records.return_value = True

    # Run the test
    main.run(requests_mock, table, logger)

    # Check the results
    print('After:')
    dump_dynamo(table)

    assert dynamo.get_db_value(table, dynamo.SCAN_BATCH_COMPLETED) == False
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING) == False
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_ID) == 6
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP) == LAST_UPDATED_RECORD_TIMESTAMP_6
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP) == BATCH_BOUNDARY_TIMESTAMP_4
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP) == BATCH_BOUNDARY_TIMESTAMP_7


@mock_dynamodb2
@patch('bookshare_shared.record_handling.get_bookshare_page')
@patch('bookshare_shared.record_handling.is_batch_complete')
@patch('bookshare_shared.record_handling.send_records')
def test_end_diff_batch(mock_send_records, mock_is_batch_complete, mock_get_bookshare_page,
                              requests_mock):
    """
    Close out a batch
    """
    # Set up the data

    table = test_helpers.create_dynamo_table(dynamo_config.DYNAMODB_LOADER_TABLE)

    # State at end of a batch
    dynamo.set_db_value(table, dynamo.SCAN_BATCH_COMPLETED, False)
    dynamo.set_db_value(table, dynamo.SCAN_RUNNING, False)
    dynamo.set_db_value(table, dynamo.LAST_UPDATED_RECORD_ID, 6)
    dynamo.set_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP, LAST_UPDATED_RECORD_TIMESTAMP_6)
    dynamo.set_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP, BATCH_BOUNDARY_TIMESTAMP_4)
    dynamo.set_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP, BATCH_BOUNDARY_TIMESTAMP_7)
    print('Before:')
    dump_dynamo(table)
    mock_is_batch_complete.return_value = True
    mock_get_bookshare_page.return_value = {
        'titles': [{'lastUpdated': LAST_UPDATED_RECORD_TIMESTAMP_5, 'bookshareId': 5}]}
    mock_send_records.return_value = True

    # Run the test
    main.run(requests_mock, table, logger)

    # Check the results
    print('After:')
    dump_dynamo(table)

    assert dynamo.get_db_value(table, dynamo.SCAN_BATCH_COMPLETED) == True
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING) == False
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_ID) == 5
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP) == LAST_UPDATED_RECORD_TIMESTAMP_5
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP) == BATCH_BOUNDARY_TIMESTAMP_7
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP) is None

#-- Tests of supporting functions

@mock_dynamodb2
@patch('bookshare_shared.record_handling.get_first_record')
def test_set_batch_boundary_head(mock_get_first_record, requests_mock):
    # Set up the data
    table = test_helpers.create_dynamo_table(dynamo_config.DYNAMODB_LOADER_TABLE)
    dynamo.set_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP, BATCH_BOUNDARY_TIMESTAMP_2)

    print('Before:')
    dump_dynamo(table)
    mock_get_first_record.return_value = {'lastUpdated': BATCH_BOUNDARY_TIMESTAMP_1}

    # Run the test
    record_handling.save_batch_boundary_head(requests_mock, table)

    # Check the results
    print('After:')
    dump_dynamo(table)

    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP) == BATCH_BOUNDARY_TIMESTAMP_2
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP) == BATCH_BOUNDARY_TIMESTAMP_1


@mock_dynamodb2
def test_update_batch_boundary():
    # Set up the data
    table = test_helpers.create_dynamo_table(dynamo_config.DYNAMODB_LOADER_TABLE)

    dynamo.set_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP, BATCH_BOUNDARY_TIMESTAMP_1)
    print('Before:')
    dump_dynamo(table)

    # Run the test
    record_handling.save_updated_batch_boundary(table)

    print('After:')
    dump_dynamo(table)

    # Check the results
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP) == BATCH_BOUNDARY_TIMESTAMP_1
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP) is None


#-- Helper functions

def dump_dynamo(table):
    print('Batch completed: ' + str(dynamo.get_db_value(table, dynamo.SCAN_BATCH_COMPLETED)))
    print('Scan running: ' + str(dynamo.get_db_value(table, dynamo.SCAN_RUNNING)))
    print('Last updated record id: ' + str(dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_ID)))
    print('Last updated record timestamp: ' + str(dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP)))
    print('Scan running total source: ' + str(dynamo.get_db_value(table, dynamo.SCAN_RUNNING_TOTAL_SOURCE)))
    print('Scan running total federated: ' + str(dynamo.get_db_value(table, dynamo.SCAN_RUNNING_TOTAL_FEDERATED)))
    print('Batch boundary TAIL timestamp: ' + str(dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP)))
    print('Batch boundary HEAD timestamp: ' + str(dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP)))