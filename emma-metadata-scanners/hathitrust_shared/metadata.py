import re
import pyisbn
import logging
from hathitrust_shared import metadata_constants
from datetime import datetime
from shared.helpers import exists, listify, stringify, get_language

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def ingestible_record(record):
    """
    Book format titles with rights that someone can access are ingestible. Everything else is not.
    """
    ingestible = exists(record, 'bib_fmt') and record['bib_fmt'] == 'BK'
    ingestible = ingestible and exists(record, 'rights') and record['rights'] not in ['nobody', 'supp']
    return ingestible

def transform_record(record):
    """
    Copy fields from the HathiTrust record
    to the EMMA Federated Index ingestion record.
    """
    emma_record = {}
    emma_record['emma_repository'] = 'hathiTrust'

    try:
        if exists(record, 'content_provider_code') and exists(
                metadata_constants.INSTITUTION_MAP, record['content_provider_code']):
            emma_record['emma_collection'] = listify(metadata_constants.INSTITUTION_MAP[record['content_provider_code']])
        if exists(record, 'htid'):
            recId = str(record['htid'])
            emma_record['emma_repositoryRecordId'] = recId
            emma_record['emma_retrievalLink'] = metadata_constants.ITEM_URL + recId
            emma_record['emma_webPageLink'] = metadata_constants.ITEM_URL + recId
        if not_empty(record, 'title'):
            emma_record['dc_title'] = record['title']
        emma_record['dc_identifier'] = get_identifiers(record)
        if not_empty(record, 'author'):
            emma_record['dc_creator'] = listify(record['author'])
        if not_empty(record, 'description'):
            emma_record['dc_description'] = stringify(record['description'])
        publisher, date = get_publisher_and_date(record)
        if date is not None and len(date) > 0:
            emma_record['dcterms_dateCopyright'] = date
        if publisher is not None and len(publisher) > 0:
            emma_record['dc_publisher'] = publisher
        rights = get_rights(record)
        if rights is not None:
            emma_record['dc_rights'] = rights
        lang = get_lang(record)
        if lang is not None:
            emma_record['dc_language'] = lang
        if not_empty(record, 'rights_timestamp'):
            emma_record['dcterms_dateAccepted'] = get_date_accepted(record)
        emma_record['dc_format'] = 'pdf'
        emma_record['s_accessMode'] = ['visual', 'textual']
        emma_record['s_accessModeSufficient'] = ['visual', 'textual']
        truncate_all_fields(emma_record)
        return emma_record
    except Exception:
        logger.exception("Exception thrown in transform_record")
        logger.error(record)


def get_lang(record):
    lang = None
    if not_empty(record, 'lang'):
        iso_lang = get_language(record['lang'])
        if iso_lang is not None and len(iso_lang) > 0:
            lang = iso_lang
    if lang is not None:
        lang = listify(lang)
    return lang

def truncate_all_fields(record):
    """
    Even ElasticSearch has field length limits, which are tested by the length of some fields in the metadata file.
    This truncates all string fields to a reasonable maximum which ElasticSearch can handle.
    """
    for key in record:
        value = record[key]
        if isinstance(value, list):
            new_value = [trunc_if_string(item) for item in value]
        elif isinstance(value, str):
            new_value = trunc_if_string(value)
        record[key] = new_value


def trunc_if_string(item):
    if isinstance(item, str):
        return item[:metadata_constants.MAX_STRING_LENGTH]
    else:
        return item


def not_empty(record, field):
    return exists(record, field) and len(record[field]) > 0


def separate_imprint(imprint):
    """
    Some Internet Archive records have nonstandard characters after the LCCN
    """
    groups = re.match(metadata_constants.IMPRINT_REGEX_PATTERN, imprint)
    if groups is not None and len(groups.groups()) > 1 :
        return groups.group(1), groups.group(2)
    return None, None


def get_date_accepted(record):
    if exists(record, 'rights_timestamp'):
        timestamp = record['rights_timestamp']
        timestamp_object = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        return timestamp_object.isoformat()


def get_publisher_and_date(record):
    publisher = None
    date = None
    if not_empty(record, 'imprint'):
        publisher, date = separate_imprint(record['imprint'])
    if date is None and exists (record, 'rights_date_used'):
        date = record['rights_date_used']
    return publisher, date


def get_rights(record):
    if not_empty(record, 'rights') and not_empty(metadata_constants.RIGHTS_MAP, record['rights']):
        return metadata_constants.RIGHTS_MAP[record['rights']]


def get_identifiers(record):
    """
    Look in the search result record and the get_item record to try to find standard identifiers
    """
    id_fields = {'isbn': 'isbn', 'oclc_num': 'oclc', 'lccn': 'lccn', 'issn': 'issn'}
    trail_patterns = {'isbn': metadata_constants.ISBN_TRAIL_REGEX_PATTERN,
                      'oclc_num': metadata_constants.OCLC_LCCN_TRAIL_REGEX_PATTERN,
                      'lccn': metadata_constants.OCLC_LCCN_TRAIL_REGEX_PATTERN,
                      'issn': metadata_constants.ISSN_TRAIL_REGEX_PATTERN}
    identifiers = []
    add_isbn_13_to_dict(record)
    for field_key in id_fields:
        identifiers.extend(get_std_ids(record, field_key, id_fields[field_key], trail_patterns[field_key]))
    identifiers = list(set(identifiers))
    return identifiers


def get_std_ids(record, infield, outfield, pattern):
    """
    Normalize standard IDs
    """
    "^((isbn|upc|issn):[0-9Xx]{8,14}|lccn:[a-zA-Z0-9]{1,12}|oclc:[0-9]{1,14})$"
    identifiers = []
    if exists(record, infield) and len(record[infield]) > 0:
        std_ids = listify(record[infield])
        for std_id in std_ids:
            std_id = remove_trailing_letters(std_id, pattern)
            # Remove non alphanumeric characters
            std_id = re.sub(r'[^0-9a-zA-Z]', '', std_id)
            # Add prefix like isbn: depending on field name
            identifier = outfield + ":" + std_id
            if re.search(metadata_constants.STD_ID_VALIDATION_PATTERN, identifier) is not None:
                identifiers.append(identifier)
    return identifiers

def add_isbn_13_to_dict(record):
    """
    If the existing ISBN is not a 13-digit ISBN, attempt to get one.
    """
    if exists(record, 'isbn'):
        original_isbn = record['isbn']
        original_isbn = remove_trailing_letters(original_isbn, metadata_constants.ISBN_TRAIL_REGEX_PATTERN)
        original_isbn = re.sub(r'[^0-9Xx]', '', original_isbn)
        if len(original_isbn) > 1 and len(original_isbn) < 13:
            try:
                isbn_13 = pyisbn.convert(original_isbn)
                record['isbn'] = [original_isbn, isbn_13]
            except:
                logger.error("Can't convert isbn " + str(original_isbn) + " in record " +  str(record['htid']))

def remove_trailing_letters(dirty_id, regex_pattern):
    """
    Some records have nonstandard characters after the standard identifiers
    """
    groups = re.match(regex_pattern, dirty_id)
    if groups is not None and len(groups.groups()) > 0 :
        return groups.group(1)
    return dirty_id