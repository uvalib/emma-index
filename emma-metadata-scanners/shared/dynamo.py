from datetime import datetime, timedelta
from shared import helpers, dynamo_config, emma_config
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SCAN_BATCH_COMPLETED = dynamo_config.STATUS_TABLE_PREFIX + 'SCAN_BATCH_COMPLETED'
BATCH_BOUNDARY_TAIL_TIMESTAMP = dynamo_config.STATUS_TABLE_PREFIX + 'BATCH_BOUNDARY_TAIL_TIMESTAMP'
BATCH_BOUNDARY_HEAD_TIMESTAMP = dynamo_config.STATUS_TABLE_PREFIX + 'BATCH_BOUNDARY_HEAD_TIMESTAMP'
LAST_UPDATED_RECORD_ID = dynamo_config.STATUS_TABLE_PREFIX + 'LAST_UPDATED_RECORD_ID'
LAST_UPDATED_RECORD_TIMESTAMP = dynamo_config.STATUS_TABLE_PREFIX + 'LAST_UPDATED_RECORD_TIMESTAMP'
SCAN_RUNNING = dynamo_config.STATUS_TABLE_PREFIX +'SCAN_RUNNING'
SCAN_NEXT_TOKEN = dynamo_config.STATUS_TABLE_PREFIX +'SCAN_NEXT_TOKEN'
SCAN_RUNNING_TOTAL_SOURCE = dynamo_config.STATUS_TABLE_PREFIX +'SCAN_RUNNING_TOTAL_SOURCE'
SCAN_RUNNING_TOTAL_FEDERATED = dynamo_config.STATUS_TABLE_PREFIX +'SCAN_RUNNING_TOTAL_FEDERATED'


def initialize_db_flag(table, flag_name, init):
    table.put_item(
        Item={
            'name': flag_name,
            'val': init
        }
    )


def get_db_value(table, attr_name):
    response = table.get_item(
    Key={
        'name': attr_name
    })
    if 'Item' in response and len(response['Item']) > 0:
        item = response['Item']
        return item['val']
    else:
        return 


def set_db_value(table, attr_name, attr_value):
    table.put_item(
        Item={
            'name': attr_name,
            'val': attr_value
        }
    )


def delete_db_value(table, attr_name):
    table.delete_item(
        Key={
            'name': attr_name
        }
    )


def start_running(table, flag_name):
    table.update_item(
        Key={
            'name': flag_name
        },
        UpdateExpression='SET val = :val1, started = :val2',
        ExpressionAttributeValues={
            ':val1': True,
            ':val2': helpers.get_today_iso8601_datetime_pst()
        }
    )


def end_running(table, flag_name):
    table.update_item(
        Key={
            'name': flag_name
        },
        UpdateExpression='SET val = :val1',
        ExpressionAttributeValues={
            ':val1': False
        }
    )
    table.update_item(
        Key={
            'name': flag_name
        },
        UpdateExpression='REMOVE started'
    )


def check_running(table, flag_name):
    """
    Check to see if the job is already running.
    If the job is running but started more than 15 minutes ago, we can mark it done because lambda functions are limited to 15 minutes.

    """
    running = False
    response = table.get_item(
        Key={
            'name': flag_name
        })
    if 'Item' in response and len(response['Item']) > 0:
        item = response['Item']
        running = item['val']
        if running:
            if 'started' in item:
                started = datetime.fromisoformat(item['started'])
                logger.info("Current run started " + str(started))
                now = helpers.get_now_datetime_pst()
                logger.info("Current time is     " + str(now))
                # If it's been running more than 15 minutes we can mark it done
                minutes_ago = (now - started) // timedelta(minutes=1)
                logger.info('Minutes elapsed: ' + str(minutes_ago))
                if minutes_ago > emma_config.INTERVAL_IN_MIN:
                    logger.info("Marking old job done.")
                    end_running(table, flag_name)
                    running = False
           
    else:
        initialize_db_flag(table, flag_name, False)

    return running


def check_batch_completed(table, flag_name):
    completed = True
    stored_value = get_db_value(table, flag_name)
    if stored_value is not None:
        completed = stored_value
    else:
        initialize_db_flag(table, flag_name, True)

    return completed


def update_counts(table, source_records, fed_records):
    """
    Update our count of records processed in the Dynamo DB table.
    """
    previous_source_records = get_db_value(
        table, SCAN_RUNNING_TOTAL_SOURCE)
    previous_fed_records = get_db_value(
        table, SCAN_RUNNING_TOTAL_FEDERATED)

    if previous_source_records is None:
        previous_source_records = 0
    if previous_fed_records is None:
        previous_fed_records = 0
    source_records = source_records + previous_source_records
    fed_records = fed_records + previous_fed_records
    set_db_value(table, SCAN_RUNNING_TOTAL_SOURCE, source_records)
    set_db_value(table, SCAN_RUNNING_TOTAL_FEDERATED, fed_records)