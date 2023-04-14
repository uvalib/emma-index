import logging
import re
from internet_archive_shared import config
from shared.helpers import exists, listify, stringify, get_languages

logger = logging.getLogger()
logger.setLevel(logging.INFO)

IA_FORMAT_TRANSLATION = {
    "EPUB": "epub",
    "Text PDF": "pdf",
    "Grayscale LuraTech PDF": "grayscalePdf",
    "Word Document": "word"
}

STD_ID_CLEANUP_REGEX = r'([a-zA-Z]{0,3}[0-9Xx\-]{1,14})[^0-9x]*'
ARCHIVE_ORG_URL = "https://archive.org"
DOWNLOAD_URL = ARCHIVE_ORG_URL + "/download/"
DETAILS_URL = ARCHIVE_ORG_URL + "/details/"


def transform_records(records, session):
    """
    Transform a list of Internet Archive records into EMMA Federated Index ingestion records.
    """
    emma_record_list = []
    for incoming_record in records:
        if exists(incoming_record, 'identifier'):
            ia_item = session.get_item(str(incoming_record['identifier']))
            emma_records = transform_record(incoming_record, ia_item)
            if emma_records is None or len(emma_records) < 1:
                msg = str(incoming_record['identifier']) + " yielded no loadable records."
                if exists(incoming_record, 'format'):
                    msg = msg + " Available formats: " + ','.join(incoming_record['format'])
                logger.info(str(incoming_record['identifier']) + " yielded no loadable records.")
            emma_record_list.extend(emma_records)
        else:
            logger.info("Skipped record with no identifier")
    return emma_record_list


def transform_record(incoming_record, ia_item):
    """
    Transform Internet Archive search result and get_item result to EMMA Federated Index ingestion records
    """
    transformed_records = []
    format_file_map = get_format_file_map(ia_item.files)
    if exists(incoming_record, 'format'):
        incoming_formats = incoming_record['format']
        for incoming_format in incoming_formats:
            if incoming_format in IA_FORMAT_TRANSLATION:
                emma_record = get_title_field_record(incoming_record, ia_item)
                if incoming_format in format_file_map:
                    emma_record['emma_retrievalLink'] = get_download_file_link(incoming_format, incoming_record, format_file_map)
                emma_record['dc_format'] = IA_FORMAT_TRANSLATION[incoming_format]
                transformed_records.append(emma_record)
        '''
        According to email from Internet Archive, these are indicators of automatically created 
        EPUB and DAISY files.  (Andrea Mills <andrea@archive.org> 2020-01-02)
        '''
        if 'DjVuTXT' in incoming_formats and 'Abbyy GZ' in incoming_formats:
            transformed_records.append(get_autogen_daisy(incoming_record, ia_item))
            if 'EPUB' not in incoming_formats:
                transformed_records.append(get_autogen_epub(incoming_record, ia_item))

    return transformed_records

def get_format_file_map(file_list):
    """
    Take the list of files and return of map of format to file
    """
    return dict((i['format'], i) for i in file_list)

def get_download_file_link(incoming_format, incoming_record, format_file_map):
    if exists(incoming_record, 'identifier') and exists(format_file_map, incoming_format) \
        and exists(format_file_map[incoming_format], 'name'):

        return DOWNLOAD_URL + incoming_record['identifier'] + "/" + format_file_map[incoming_format]['name']

def get_title_field_record(record, ia_item):
    """
    Copy all title-level fields (as opposed to artifact-level) from the Internet Archive record
    to the EMMA Federated Index ingestion record.
    AKA "Item Level" in Internet Archive terminology.
    """
    emma_record = {}
    emma_record['emma_repository'] = config.IA_REPOSITORY_NAME
    emma_record['emma_repositoryMetadataUpdateDate'] = record[config.DATE_BOUNDARY_FIELD]
    try:
        if exists(record, 'collection'):
            emma_record['emma_collection'] = listify(record['collection'])
        if exists(record, 'identifier'):
            recId = str(record['identifier'])
            emma_record['emma_repositoryRecordId'] = recId
            emma_record['emma_retrievalLink'] = DOWNLOAD_URL + recId
            emma_record['emma_webPageLink'] = DETAILS_URL + recId
        if exists(record, 'title'):
            emma_record['dc_title'] = record['title']
        emma_record['dc_identifier'] = get_identifiers(record, ia_item)
        if exists(record, 'related-external-id'):
            emma_record['dc_relation'] = get_related_identifiers(record)
        if exists(record, 'creator'):
            emma_record['dc_creator'] = listify(record['creator'])
        if exists(record, 'description'):
            emma_record['dc_description'] = stringify(record['description'])
        if exists(record, 'subject'):
            emma_record['dc_subject'] = listify(record['subject'])
        if exists(record, 'date'):
            emma_record['dcterms_dateCopyright'] = record['date'][:4]
        if exists(record, 'publisher'):
            emma_record['dc_publisher'] = stringify(record['publisher'])
        if exists(record, 'rights'):
            emma_record['dc_rights'] = get_rights(record)
        if exists(record, 'publicdate'):
            emma_record['dcterms_dateAccepted'] = record['publicdate']
        if exists(record, 'language'):
            emma_record['dc_language'] = get_languages(record)
        return emma_record
    except Exception as e:
        logger.exception("Exception thrown in get_title_field_record")
        logger.error(record)


def get_autogen_daisy(record, ia_item):
    """
    Inject data known to be true about autogenerated Internet Archive DAISY file
    """
    emma_record = get_title_field_record(record, ia_item)
    emma_record['dc_format'] = 'daisy'
    # Format of DAISY retrieval link per email Andrea Mills <andrea@archive.org> 1/17/2020
    emma_record['emma_retrievalLink'] = DOWNLOAD_URL + record['identifier'] + "/" + record['identifier'] + "_daisy.zip"

    return emma_record


def get_autogen_epub(record, ia_item):
    """
    Inject data known to be true about autogenerated Internet Archive EPUBs
    """
    emma_record = get_title_field_record(record, ia_item)
    emma_record['dc_format'] = 'epub'
    '''
    These fields are taken directly from an autogenerated Internet Archive EPUB.
    '''
    emma_record['s_accessibilityFeature'] = [
        'printPageNumbers', 'tableOfContents']
    emma_record['s_accessMode'] = ['visual', 'textual']
    emma_record['s_accessModeSufficient'] = ['visual', 'textual']
    emma_record['s_accessibilityHazard'] = [
        'noFlashingHazard', 'noMotionSimulationHazard', 'noSoundHazard']
    emma_record['s_accessibilityControl'] = ['fullKeyboardControl',
                                             'fullMouseControl', 'fullSwitchControl', 'fullTouchControl', 'fullVoiceControl']
    emma_record['s_accessibilitySummary'] = 'The publication was generated using automated character recognition, therefore it may not be an accurate rendition of the original text, and it may not offer the correct reading sequence.This publication is missing meaningful alternative text.The publication otherwise meets WCAG 2.0 Level A.'
    emma_record['emma_formatVersion'] = "3.0"
    # Format of DAISY retrieval link per email Andrea Mills <andrea@archive.org> 1/17/2020
    emma_record['emma_retrievalLink'] = DOWNLOAD_URL + record['identifier'] + "/" + record['identifier'] + ".epub"

    return emma_record


def get_related_identifiers(record):
    """
    Using the related-external-id field in search results, create related identifier list
    """
    if exists(record, 'related-external-id'):
        identifiers = []
        related_ids = listify(record['related-external-id'])
        for related_id in related_ids:
            if related_id.startswith('urn:'):
                if related_id.startswith('urn:isbn:') or related_id.startswith('urn:oclc:') or related_id.startswith('urn:lccn:'):
                    identifiers.append(related_id[4:])
        return identifiers


def get_identifiers(record, item):
    """
    Look in the search result record and the get_item record to try to find standard identifiers
    """
    id_fields = ['isbn', 'oclc', 'lccn']
    identifiers = []
    for id_field in id_fields:
        identifiers.extend(get_std_ids(record, id_field))
        identifiers.extend(get_std_ids(item.metadata, id_field))
    identifiers = list(set(identifiers))
    return identifiers


def get_std_ids(record, field):
    """
    Normalize standard IDs
    """
    identifiers = []
    if exists(record, field):
        std_ids = listify(record[field])
        for std_id in std_ids:
            # Remove prefix like isbn: if it exists
            if std_id.startswith(field + ":"):
                std_id = std_id[5:]
            # Remove trailing characters after last digit in a alphanumeric sequence
            std_id = remove_trailing_letters(std_id)
            # Remove non alphanumeric characters
            std_id = re.sub(r'[^0-9a-zA-Z]', '', std_id)
            # Add prefix like isbn: depending on field name
            identifiers.append(field + ":" + std_id)
    return identifiers


def remove_trailing_letters(dirty_id):
    """
    Some Internet Archive records have nonstandard characters after the LCCN
    """
    groups = re.match(STD_ID_CLEANUP_REGEX, dirty_id)
    if groups is not None and len(groups.groups()) > 0 :
        return groups.group(1)
    return dirty_id


def get_rights(record):
    """
    Convert to our controlled rights vocabulary (creativeCommons,publicDomain)
    I didn't see any values for "copyrighted" so that's not included here yet.
    """
    if exists(record, 'rights'):
        rights = record['rights']
        if re.match(r'^CC', rights, re.IGNORECASE):
            return 'creativeCommons'
        elif re.match(r'creative commons', rights, re.IGNORECASE):
            return 'creativeCommons'
        elif re.match(r'public', rights, re.IGNORECASE):
            return 'publicDomain'



