import json
import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry 

from internet_archive_shared import config, metadata
from shared import dynamo
from shared.dynamo import get_db_value, set_db_value, delete_db_value, update_counts
from shared.helpers import batch, exists, get_now_iso8601_datetime_utc

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_transform_send(session, table):
    """
    Get records from IA
    Transform the records to EMMA format
    Send them to EMMA
    """
    num_records = 0
    try:
        ia_response = get_next_scrape_response(table)
        if (ia_response.status_code == 200):
            ia_json = ia_response.json()
            ia_records = null_safe_get_items(ia_json)
            emma_records = metadata.transform_records(ia_records, session)
            num_records = len(emma_records)
            if len(emma_records) > 0:
                logger.info("Sending " + str(num_records) + " records to ingestion endpoint in batches.")
                batch_to_ingestion(emma_records)
                on_success(table, ia_json, ia_records)
            if is_diff_batch_complete(ia_json):
                set_db_value(table, dynamo.SCAN_BATCH_COMPLETED, True)
                record_update_batch_boundary(table)
            update_counts(table, len(ia_records), num_records)
        else:
            logger.error("Internet Archive scrape API returned: " + str(ia_response.status_code))
            logger.error(ia_response.content)
    except:
        logger.exception("Transform and send failed. This set will be retried.")
    return num_records


def on_success(table, ia_json, ia_records):
    """
    If the submission to EMMA ingestion is successful, update our records
    """
    last_record = ia_records[-1]
    first_record = ia_records[0]
    logger.info("First record in page dated " +
                str(first_record[config.DATE_BOUNDARY_FIELD]))
    logger.info("Last record scanned is now " +
                str(last_record['identifier']) + " last indexed " + str(last_record[config.DATE_BOUNDARY_FIELD]))
    if exists(ia_json, 'cursor'):
        set_db_value(table, dynamo.SCAN_NEXT_TOKEN, ia_json['cursor'])
    else:
        delete_db_value(table, dynamo.SCAN_NEXT_TOKEN)

    if exists(last_record, config.DATE_BOUNDARY_FIELD):
        set_db_value(
            table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP, last_record[config.DATE_BOUNDARY_FIELD])
    else:
        logger.error("Possibly fatal error, no " +
                     config.DATE_BOUNDARY_FIELD + " in the last record.")

    set_db_value(table, dynamo.LAST_UPDATED_RECORD_ID, last_record['identifier'])



def null_safe_get_items(ia_json):
    items = []
    if exists(ia_json, 'items'):
        items = ia_json['items']
    return items


def build_query(table):
    batch_boundary_date = get_db_value(
        table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP)
    next_batch_boundary_date = get_db_value(
        table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP)

    collection_list = config.IA_COLLECTION_LIST
    collection_clause = " OR ".join(collection_list)
    formats_list = list(filter(None, config.IA_FORMATS))

    query = "_exists_:" + config.DATE_BOUNDARY_FIELD + " AND collection:(" + collection_clause + ") AND mediatype:(texts)"

    if formats_list is not None and len(formats_list) > 0:
       formats = " AND ".join(formats_list)
       formats_clause = " AND format:(" + formats + ")"
       query = query + formats_clause
    if batch_boundary_date is None or len(batch_boundary_date) == 0:
        logger.info("No last batch boundary found, running to end of records")
        lower_limit = 'NULL'
    else:
        lower_limit = str(batch_boundary_date)

    if next_batch_boundary_date is None or len(next_batch_boundary_date) == 0:
        logger.error("No next batch boundary found, this is a fatal condition")
        upper_limit = 'NULL'
    else:
        upper_limit = str(next_batch_boundary_date)

    if lower_limit != 'NULL' or upper_limit != 'NULL':
        query = query + " AND " + config.DATE_BOUNDARY_FIELD + ":[" + lower_limit + " TO " + upper_limit + "]"

    return query


def get_next_scrape_response(table):
    """
    Get the next page from the Internet Archive scrape API
    """
    query = build_query(table)
    next_page = get_db_value(table, dynamo.SCAN_NEXT_TOKEN)

    params = config.SEARCH_PARAMS.copy()
    params['q'] = query

    if next_page is not None:
        params['cursor'] = next_page

    logger.info("Scraping next page: " + json.dumps(params))

    ia_response = requests.post(config.IA_SCRAPE_URL, params=params, headers=config.HEADERS)

    return ia_response


def record_set_next_batch_boundary(table):
    """
    Save the Internet Archive API date boundary for the batch after the current one
    """
    now_utc = get_now_iso8601_datetime_utc()
    set_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP, now_utc)


def record_update_batch_boundary(table):
    """
    When one batch is done, update the batch record boundary in the Dynamo DB database
    """
    boundary_date = get_db_value(
        table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP)
    if boundary_date is not None:
        set_db_value(
            table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP, boundary_date)
    delete_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP)
    # Reset query paging
    delete_db_value(table, dynamo.SCAN_NEXT_TOKEN)


def is_diff_batch_complete(ia_response):
    """
    Check to see if the current batch is complete.  The current batch runs until it hits
    the previous record boundary, or until there are no more records.
    """
    return not exists(ia_response, 'cursor')


def get_last_updated_date_list(records):
    """
    Extracts the list of updated dates
    """
    return list(map(lambda x: x[config.DATE_BOUNDARY_FIELD], records))


def batch_to_ingestion(emma_records):
    """
    Sends in smaller batches to ingestion endpoint to prevent timeout.
    """
    emma_headers = {'x-api-key': config.EMMA_API_KEY}
    with requests.Session() as s:
        retries = Retry(total=config.EMMA_INGESTION_RETRY, backoff_factor=.2, status_forcelist=Retry.RETRY_AFTER_STATUS_CODES, raise_on_status=False)
        s.mount('https://', HTTPAdapter(max_retries=retries))
        for records in batch(emma_records, config.EMMA_INGESTION_LIMIT):
            logger.info("Sending smaller batch of  " + str(len(records)) + " records to ingestion endpoint")
            emma_response = s.put(config.EMMA_INGESTION_URL,
                                  headers=emma_headers, json=records)
            if emma_response.status_code == 202:
                logger.info("Batch of " + str(len(records)) + " successful.")
            elif emma_response.status_code == 207:
                logger.info(
                    "Partial failure.  This set will not be retried.  Status code: " + str(
                        emma_response.status_code) + "  Errors: " + str(
                        emma_response.text))
            elif emma_response.status_code in Retry.RETRY_AFTER_STATUS_CODES :
                logger.error("This smaller set returned an error after exhausting " + str(config.EMMA_INGESTION_RETRY) + 
                             " retries. Ingestion returned failure: " + str(emma_response.status_code) + "  " + str(emma_response.text))
                logger.info("Records")
                logger.info(json.dumps(records))
            else :
                logger.error("This smaller set returned an error. Ingestion returned failure: " +
                             str(emma_response.status_code) + "  " + str(emma_response.text))
                logger.info("Records")
                logger.info(json.dumps(records))

