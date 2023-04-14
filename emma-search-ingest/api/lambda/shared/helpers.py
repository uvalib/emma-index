import json
import pytz
from shared import config
from datetime import datetime, timezone, timedelta
from elasticsearch_dsl.utils import AttrList

def get_doc_id(doc) -> str:
    """
    Create a document ID from the properties we expect to be unique to a metadata record
    """
    if 'emma_recordId' in doc:
        return doc['emma_recordId']
    doc_id = doc['emma_repository'] + "-" + \
        doc['emma_repositoryRecordId'] + "-" + doc['dc_format']
    if 'emma_formatVersion' in doc:
        doc_id = doc_id + "-" + doc['emma_formatVersion']
    return doc_id


def get_doc_id_prefix(doc) -> str:
    """
    Create a document ID prefix (ID without format) from the properties we expect to be unique to a metadata record
    """
    if 'emma_recordId' in doc:
        parts =  doc['emma_recordId'].split('-')
        parts = parts[0:-1]
        return '-'.join(parts)
    doc_id = doc['emma_repository'] + "-" + \
        doc['emma_repositoryRecordId']
    return doc_id


def listify_record(record):
    """
    Make sure that properties that are defined as lists are returned as lists, even if there is only one value 
    in the list.
    """
    list_types = ['emma_formatFeature', 'emma_collection', 's_accessibilityControl', 's_accessibilityFeature',
                  's_accessibilityHazard', 's_accessibilityAPI', 's_accessMode', 's_accessModeSufficient', 'dc_subject',
                  'dc_relation', 'dc_identifier', 'dc_creator', 'dc_language',
                  'rem_remediatedAspects', 'rem_remediatedBy', 'rem_metadataSource']
    for list_type in list_types:
        if list_type in record: 
            record[list_type] = listify(record[list_type])
    return record


def listify(prop):
    """
    If a single property is not  a list but should be, convert to a single-element list
    """
    return prop if isinstance(prop, list) or isinstance(prop, AttrList) else [prop]


def get_json_list(incoming_data, errors):
    """
    Check that the incoming data is a JSON-formatted object containing
    a record list and return it as a list data structure if it is
    If it is not a JSON-formatted list, return nothing and update error list
    """
    try:
        json_object = json.loads(incoming_data)
    except ValueError as e:
        errors['body'] = ['Submitted data is not valid JSON'] + list(e.args)
        return 

    if isinstance(json_object, list):
        if len(json_object) > config.INGESTION_RECORD_LIMIT:
            errors['body'] = ['Submitted data contains more than ' + str(config.INGESTION_RECORD_LIMIT) + ' records'] 
            return
        elif len(json_object) == 0:
            errors['body'] = ['Request list does not contain any records'] 
            return
        else:
            return json_object
            
    errors['body'] = ['Submitted data is not a list']
    return 


def string_or_nothing(result_obj, errors_dict) ->str:
    """
    Format errors and results as a JSON string.
    If there are no results or errors, make the body empty.
    """
    if isinstance(result_obj, dict):
        if len(result_obj) == 0 and len(errors_dict) == 0:
            # Empty message body for successful upsert and delete
            result_str = ''
        elif isinstance(errors_dict, dict):
            # Merge non-fatal "Not Found" messages with errors
            result_dict = {**errors_dict, **result_obj}
            result_str = json.dumps(result_dict)
        else:
            result_str = json.dumps(result_obj)
    else:
        # Return get operation results
        if len(errors_dict) == 0:
            result_str = json.dumps(result_obj)
        else:
            result_str = json.dumps(errors_dict)
    return result_str


def exists(record, field_name):
    return field_name in record and record[field_name] is not None


def safe_del(record, field_name):
    if exists(record, field_name):
        del record[field_name]


def get_multi_param(param, query_string_params, multi_string_params):
    """
    In a somewhat bizarre design choice, AWS API gateway returns two separate query parameter lists, one with single valued
    params, the other with multi-valued.  What's bizarre is the first value for every multi-valued param will also
    appear in the single valued list "queryStringParameters".
    """
    result = None
    if exists(multi_string_params, param):
        param_list = list(filter(None, multi_string_params[param]))
        if len(param_list) > 0:
            result = multi_string_params[param]
    elif exists(query_string_params, param):
        if len(query_string_params[param]) > 0:
            result = listify(query_string_params[param])
    return result

"""
Date/Time 
We'll work in PST since that's Bookshares Point of View
"""
def get_now_iso8601_date_pst():
    utc_dt = datetime.now(timezone.utc)
    PST = pytz.timezone('US/Pacific')
    return utc_dt.astimezone(PST).date().isoformat()

def get_now_datetime_pst():
    utc_dt = datetime.now(timezone.utc)
    PST = pytz.timezone('US/Pacific')
    return utc_dt.astimezone(PST)

def get_today_iso8601_datetime_pst():
    return get_now_datetime_pst().isoformat()

def get_now_iso8601_datetime_utc():
    utc_dt = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return utc_dt