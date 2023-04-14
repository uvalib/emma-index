import json
import logging

import requests

from bookshare_shared import config, metadata
from shared import dynamo
from shared.dynamo import get_db_value, set_db_value, delete_db_value, update_counts
from shared.helpers import exists

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def single_run(session, table, limit, pages):
    """
    The loop that runs for a single lambda run
    """

    params = setup_run_params(table, limit)
    next_token = ''
    page_count = 0
    done = False

    while page_count < pages and not done:
        try:
            if len(next_token) > 0:
                params['start'] = next_token

            json_object = get_bookshare_page(session, params, next_token)

            if json_object is not None:
                titles = json_object.get('titles', [])
                if len(titles) > 0:
                    if send_records(titles,table):
                        save_last_record_timestamp(table, titles[-1])
                    else:
                        raise Exception("Records not ingested by federated index.")

                next_token = json_object.get('next', '')

                done = is_batch_complete(titles, next_token)

        except:
            logger.exception("Retrieve, transform and send failed. This set will be retried.")
            break

        page_count = page_count + 1

    dump_new_batch_params('RUN COMPLETE', table)

    if done:
        set_db_value(table, dynamo.SCAN_BATCH_COMPLETED, True)
        save_updated_batch_boundary(table)


def get_bookshare_page(session, params, next_token):
    """
    Retrieve a page of Bookshare catalog results
    """
    if len(next_token) > 0:
        params['start'] = next_token

    r = session.get(config.BKS_BASE_URL + '/catalog',
                    params=params, headers=config.BKS_HEADERS)
    logger.info("Request to Bookshare: " + r.url)
    logger.info("Headers sent to Bookshare: " + str(r.headers))

    return get_json_object(r)


def setup_run_params(table, limit):
    """
    Set up the catalog retrieval parameters to be used in this run of the lambda function
    """

    batch_boundary_head_timestamp = get_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP)
    batch_boundary_tail_timestamp = get_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP)
    last_updated_record_timestamp = get_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP)

    logger.info("batch_boundary_head_timestamp: " + str(batch_boundary_head_timestamp))
    logger.info("batch_boundary_tail_timestamp: " + str(batch_boundary_tail_timestamp))
    logger.info("last_updated_record_timestamp: " + str(last_updated_record_timestamp))

    params = {"sortOrder": "updatedDate",
              "titleStatus": "available",
              "direction": "desc",
              "limit": limit,
              }

    '''
    Note that start and end are reversed here because we are going backwards in time through the records as a batch,
    but in an individual query we will still express the window with the start date as earlier than the end date.
    Might need to do some renaming to make this less confusing.
    '''
    if batch_boundary_head_timestamp is not None:
        logger.info("Window end is batch boundary head timestamp")
        params['endUpdatedDate'] = batch_boundary_head_timestamp
    else:
        logger.info("No HEAD timestamp.")
    if last_updated_record_timestamp is not None:
        logger.info("Window end is last updated record timestamp")
        params['endUpdatedDate'] = last_updated_record_timestamp
    if batch_boundary_tail_timestamp is not None:
        logger.info('Window start is batch boundary tail timestamp')
        params['startUpdatedDate'] = batch_boundary_tail_timestamp

    logger.info("startUpdatedDate: " + str(params.get('startUpdatedDate', None)))
    logger.info("endUpdatedDate:   " + str(params.get('endUpdatedDate', None)))

    if params.get('startUpdatedDate', None) is not None and params.get('endUpdatedDate', None) is not None:
        '''
        This should never happen, but given how confusing it can be to go back in time through the data, 
        let's throw an error if this is ever false.
        '''
        assert params.get('startUpdatedDate') <= params.get('endUpdatedDate')
    return params


def get_json_object(response):
    """
    Convert a JSON response to a Python data structure
    """
    json_object = {}
    try:
        json_object = json.loads(response.content)
    except ValueError as e:
        logger.error(response.content)
        log_and_raise(
            'Data retrieved from Bookshare V2 API is not valid JSON: ' + str(list(e.args)))
    raise_on_bookshare_messages(response.url, json.loads(response.content))
    return json_object


def send_records(records, table):
    """
    Send records to the EMMA Ingestion endpoint
    """
    emma_records = metadata.transform_records(records)
    emma_headers = {'x-api-key': config.EMMA_API_KEY}
    if len(emma_records) > 0:
        logger.info("Sending " + str(len(emma_records)) +
                    " records to ingestion endpoint")
        r = requests.put(config.EMMA_INGESTION_URL,
                         headers=emma_headers, json=emma_records)
        if str(r.status_code) in ['202', '207']:
            on_success(table, r, records, emma_records)
            return True
        else:
            logger.error("This set will be retried.  Ingestion returned failure: " +
                         str(r.status_code) + "  " + str(r.text))
            logger.info("Records")
            logger.info(json.dumps(emma_records))
            return False
    else:
        return True


def on_success(table, response, records, emma_records):
    """
    Handle successful outcome of EMMA ingestion
    """
    update_counts(table, len(records), len(emma_records))
    if response.status_code == '202':
        logger.info("Ingestion success.")
    if response.status_code == '207':
        logger.info(
            "Partial failure.  This set will not be retried.  Status code: " + str(
                response.status_code) + "  Errors: " + str(
                response.text))


def dump_new_batch_params(label, table):
    batch_boundary_head_timestamp = get_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP)
    batch_boundary_tail_timestamp = get_db_value(table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP)
    last_updated_record_timestamp = get_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP)
    logger.info(label + " batch_boundary_head_timestamp: " + str(batch_boundary_head_timestamp))
    logger.info(label + " batch_boundary_tail_timestamp: " + str(batch_boundary_tail_timestamp))
    logger.info(label + " last_updated_record_timestamp: " + str(last_updated_record_timestamp))

def save_last_record_timestamp(table, record):
    """
    Keep track of the last updated record so we know where to resume
    """
    set_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP, record['lastUpdated'])
    set_db_value(table, dynamo.LAST_UPDATED_RECORD_ID, record['bookshareId'])
    logger.info("Last processed record id " + str(record['bookshareId']) + " lastUpdated " + record['lastUpdated'])


def get_first_record(session):
    """
    Get the first record with most recent updatedDate from the Bookshare V2 API
    """
    params = {"sortOrder": "updatedDate",
              "titleStatus": "available",
              "direction": "desc",
              "limit": 1
              }
    r = session.get(config.BKS_BASE_URL + '/catalog',
                    params=params, headers=config.BKS_HEADERS)
    raise_on_bookshare_messages(r.url, json.loads(r.content))
    json_object = json.loads(r.content)
    return json_object['titles'][0]


def save_batch_boundary_head(session, table):
    """
    Save the Bookshare API timestamp boundary
    """
    record = get_first_record(session)
    if exists(record, 'lastUpdated'):
        set_db_value(
            table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP, record['lastUpdated'])
        delete_db_value(table, dynamo.LAST_UPDATED_RECORD_TIMESTAMP)
    dump_new_batch_params('NEW BATCH', table)

def save_updated_batch_boundary(table):
    """
    When one batch is done, update the batch record boundary in the Dynamo DB database
    """
    boundary_date = get_db_value(
        table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP)
    if boundary_date is not None:
        set_db_value(
            table, dynamo.BATCH_BOUNDARY_TAIL_TIMESTAMP, boundary_date)
    delete_db_value(table, dynamo.BATCH_BOUNDARY_HEAD_TIMESTAMP)
    dump_new_batch_params('NEW BATCH', table)


def is_batch_complete(records, next_token):
    """
    Check to see if the current batch is complete.  The current batch runs until it hits
    the previous record boundary, or until there are no more next tokens.
    """
    if next_token is None or len(next_token) == 0:
        logger.info("No next token, batch done.")
        return True
    if records is None or len(records) == 0:
        logger.info("No more records, batch done.")
        return True
    return False


def log_and_raise(message):
    """
    Log an error and raise it as an exception it in one step
    """
    logger.error(message)
    raise Exception(message)


def raise_on_bookshare_messages(url, json_object):
    """
    If the Bookshare V2 API returns a "messages" element in the body, that's an error that we'll raise
    """
    if 'messages' in json_object and len(json_object['messages']) > 0:
        log_and_raise("Returned from Bookshare: " +
                      str(json_object['messages']) + ' ' + url)
