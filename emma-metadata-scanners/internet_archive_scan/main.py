from internet_archive_shared import config, record_handling
from shared import helpers, dynamo
from shared.dynamo import start_running, end_running, check_running, check_batch_completed, get_db_value, set_db_value


def run(session, table, logger):
    """
    This is the main loop that makes several calls to extract, transform, and load data from
    Internet Archive into the federated index.
    It is separated out from the top-level lambda function so that the session and Dynamo DB
    can be easily mocked for testing.
    """
    logger.info("Starting Internet Archive to EMMA transfer service PST " + helpers.get_today_iso8601_datetime_pst())
        
    running = check_running(table, dynamo.SCAN_RUNNING)
    if running:
        logger.info("Full scan already running")
        return

    completed = check_batch_completed(table, dynamo.SCAN_BATCH_COMPLETED)
    if completed:
        logger.info("Starting new batch")
        record_handling.record_set_next_batch_boundary(table)
        set_db_value(table, dynamo.SCAN_BATCH_COMPLETED, False)

    start_running(table, dynamo.SCAN_RUNNING)

    logger.info('Start Running')

    records_sent = 0
    
    for i in range(1, config.IA_RETRIEVALS + 1):
        records_sent = records_sent + int(record_handling.get_transform_send(session, table))
        logger.info("Finished load " + str(i) + ", total loaded " + str(records_sent))
        if (get_db_value(table, dynamo.SCAN_BATCH_COMPLETED)):
            break

    ia_pulled = get_db_value(table, dynamo.SCAN_RUNNING_TOTAL_SOURCE)
    emma_loaded = get_db_value(table, dynamo.SCAN_RUNNING_TOTAL_FEDERATED)
    logger.info("Running total: " + str(ia_pulled) + " pulled from  "+ config.IA_REPOSITORY_NAME + " " + str(emma_loaded) + " loaded to federated index.")
    end_running(table, dynamo.SCAN_RUNNING)
    return records_sent
