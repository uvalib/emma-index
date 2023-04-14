import logging

from internetarchive import get_session
from moto import mock_dynamodb2

from internet_archive_scan import main
from internet_archive_shared import config
from shared import dynamo
from shared import dynamo_config
from tests.unit.internet_archive_scan import test_data
from tests.unit.shared import test_helpers

config.IA_PAGE_SIZE = 100


@mock_dynamodb2
def test_ia_partial_scan(requests_mock):
    config.IA_RETRIEVALS = 2

    """
    First 2 pages scan with no start token, no boundary date
    """
    # Set up the data
    test_data.setup_mock(requests_mock)
    table = test_helpers.create_dynamo_table(dynamo_config.DYNAMODB_LOADER_TABLE)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ia_session = get_session(config=config.IA_SESSION_CONFIG)

    # Run the test
    records_sent = main.run(ia_session, table, logger)

    # Check the results
    assert dynamo.get_db_value(table, dynamo.SCAN_NEXT_TOKEN) == 'GET_PAGE_3_TOKEN'
    assert dynamo.get_db_value(table, dynamo.SCAN_BATCH_COMPLETED) == False
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING) == False
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP) == '2019-08-06T18:01:36Z'
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_ID) == '1975fortiethanni0000hous'
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING_TOTAL_SOURCE) == 200
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING_TOTAL_FEDERATED) == 600
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP) is None
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP) > '2020-01-16T21:39:04Z'
    assert records_sent == 600

@mock_dynamodb2
def test_ia_resume_scan_to_end(requests_mock):
    config.IA_RETRIEVALS = 2

    """
    Full scan with token and boundary date
    """
    # Set up the data
    test_data.setup_mock(requests_mock)
    table = test_helpers.create_dynamo_table(dynamo_config.DYNAMODB_LOADER_TABLE)
    dynamo.set_db_value(table, dynamo.SCAN_NEXT_TOKEN,
                        'GET_PAGE_2_TOKEN')
    dynamo.set_db_value(table, dynamo.SCAN_BATCH_COMPLETED, False)
    dynamo.set_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP, '2020-01-16T21:39:04Z')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ia_session = get_session(config=config.IA_SESSION_CONFIG)

    # Run the test
    records_sent = main.run(ia_session, table, logger)

    # Check the results
    assert dynamo.get_db_value(table, dynamo.SCAN_NEXT_TOKEN) is None
    assert dynamo.get_db_value(table, dynamo.SCAN_BATCH_COMPLETED) == True
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING) == False
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP) == '2019-12-10T14:26:47Z'
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_ID) == '262milestoboston0000conn'
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING_TOTAL_SOURCE) == 200
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING_TOTAL_FEDERATED) == 600
    # Boundary date should timestamp be when this test runs
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP) == '2020-01-16T21:39:04Z'
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP) is None
    assert records_sent == 600


@mock_dynamodb2
def test_ia_full_scan(requests_mock):
    config.IA_RETRIEVALS = 3

    """
    All 3 pages scan with no start token, no boundary date
    """
    # Set up the data
    test_data.setup_mock(requests_mock)
    table = test_helpers.create_dynamo_table(dynamo_config.DYNAMODB_LOADER_TABLE)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ia_session = get_session(config=config.IA_SESSION_CONFIG)

    # Run the test
    records_sent = main.run(ia_session, table, logger)

    # Check the results
    assert dynamo.get_db_value(table, dynamo.SCAN_NEXT_TOKEN) is None
    assert dynamo.get_db_value(table, dynamo.SCAN_BATCH_COMPLETED) == True
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING) == False
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP) == '2019-12-10T14:26:47Z'
    assert dynamo.get_db_value(table, dynamo.LAST_UPDATED_RECORD_ID) == '262milestoboston0000conn'
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING_TOTAL_SOURCE) == 300
    assert dynamo.get_db_value(table, dynamo.SCAN_RUNNING_TOTAL_FEDERATED) == 900

    # Boundary date should timestamp be when this test runs
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP) > '2020-01-16T21:39:04Z'
    assert dynamo.get_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP) is None
    assert records_sent == 900