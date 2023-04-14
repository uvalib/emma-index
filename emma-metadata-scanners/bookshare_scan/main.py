from bookshare_shared import config, record_handling
from shared import helpers, dynamo
from shared.dynamo import start_running, end_running, check_running, check_batch_completed, get_db_value, set_db_value

"""
This is the main loop that makes several calls to extract, transform, and load data from 
Bookshare into the federated index.
It is separated out from the top-level lambda function so that the session and Dynamo DB
can be easily mocked for testing.
"""


def run(session, table, logger):

    logger.info("Starting EMMA transfer service PST " + helpers.get_today_iso8601_datetime_pst())
        
    running = check_running(table, dynamo.SCAN_RUNNING)
    if running:
        logger.info("Full scan already running")
        return

    completed = check_batch_completed(table, dynamo.SCAN_BATCH_COMPLETED)
    if completed:
        logger.info("Starting new batch")
        record_handling.save_batch_boundary_head(session, table)
        set_db_value(table, dynamo.SCAN_BATCH_COMPLETED, False)

    start_running(table, dynamo.SCAN_RUNNING)

    logger.info('Start Running')

    record_handling.single_run(session, table, config.BKS_PAGE_SIZE, config.BKS_RETRIEVALS)

    bookshare_pulled = get_db_value(table, dynamo.SCAN_RUNNING_TOTAL_SOURCE)
    emma_loaded = get_db_value(table, dynamo.SCAN_RUNNING_TOTAL_FEDERATED)
    logger.info("Running total: " + str(bookshare_pulled) + " pulled from bookshare " + str(emma_loaded) + " loaded to federated index.")
    end_running(table, dynamo.SCAN_RUNNING)
    return
