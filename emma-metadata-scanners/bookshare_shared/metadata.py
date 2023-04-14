import logging

from bookshare_shared.config import BKS_SITE
from shared.EmmaValidator import EmmaValidator
from shared.helpers import exists

logger = logging.getLogger()
logger.setLevel(logging.INFO)

BKS_FORMAT_TRANSLATION = {
    "DAISY": "daisy",
    "DAISY_AUDIO": "daisyAudio",
    "DAISY_2_AUDIO": "daisyAudio",
    "EPUB3" : "epub",
    "PDF": "pdf",
    "BRF": "brf",
    "DOCX": "word"
}

BKS_FORMAT_VERSION_TRANSLATION = {
    "DAISY_AUDIO": "1",
    "DAISY_2_AUDIO": "2",
    "EPUB3" : "3.0"
}

BKS_RESTRICTION_TRANSLATION = {
    "copyright": "copyright",
    "publicdomain": "publicDomain",
    "creativecommons" : "creativeCommons"
}

INGESTION_SCHEMA_FILE = 'shared/ingestion-record.schema.json'

emmaValidator = EmmaValidator(INGESTION_SCHEMA_FILE)


def transform_records(bks_record_list):
    """
    Transform a list of Bookshare API V2 records into EMMA Federated Index ingestion records.
    """
    emma_record_list = []
    for bks_record in bks_record_list:
        if site_ok(bks_record) and live(bks_record):
            emma_records = transform_record(bks_record)
            emma_record_list.extend(emma_records)
    return emma_record_list


def site_ok(bks_record):
    return BKS_SITE == 'bookshare' or bks_record['site'] == BKS_SITE


def live(bks_record):
    return exists(bks_record, 'available') and bks_record['available'] == True


def transform_record(bks_record):
    """
    Transform an individual Bookshare API V2 record into EMMA Federated Index ingestion records.
    Note that one record per format will come out of the transformation of the incoming record.
    """
    emma_records = []
    if exists(bks_record, 'lastUpdated') and exists(bks_record, 'bookshareId'):
        logger.info("Transforming Bookshare ID " + str(bks_record['bookshareId']) + " last updated " + bks_record['lastUpdated'])
    if exists(bks_record, 'formats'):
        artifact_map = get_artifact_map(bks_record)
        for format_obj in bks_record['formats']:
            format = format_obj['formatId']
            if format in BKS_FORMAT_TRANSLATION:
                new_record = get_title_field_record(bks_record)
                new_record['dc_format'] = BKS_FORMAT_TRANSLATION[format] 
                new_record['emma_retrievalLink'] = get_retrieval_link(bks_record, format)
                if format in BKS_FORMAT_VERSION_TRANSLATION:
                    new_record['emma_formatVersion'] = BKS_FORMAT_VERSION_TRANSLATION[format]

                # Format-specific metadata
                if format == 'DAISY':
                    add_daisy_accessibility_features(new_record, artifact_map)
                elif format == 'BRF':
                    add_brf_accessibility_features(new_record, artifact_map)
                elif format in ['DAISY_AUDIO', 'DAISY_2_AUDIO']:
                    add_daisy_audio_accessibility_features(new_record, artifact_map, format)

                if format in ['DAISY', "EPUB3", "DOCX", "PDF"]:
                    add_textual_visual(new_record)

                # Check our work against the schema
                errors = {}
                emmaValidator.validate(new_record, new_record['emma_repositoryRecordId'], errors)
                if len(errors) > 0 :
                    logger.error("Validation errors " + str(errors))
                else: 
                    emma_records.append(new_record)
    return emma_records


def get_artifact_map(bks_record):
    """
    Restructure artifact list as a map by format
    """
    if exists(bks_record, 'artifacts') and len(bks_record['artifacts']) > 0:
        return { x['format'] : x  for x in bks_record['artifacts'] }


def get_title_field_record(bks_record):
    """
    Copy all title-level fields (as opposed to artifact-level) from the Bookshare record 
    to the EMMA Federated Index ingestion record.
    """
    emma_record = {}
    emma_record['emma_repository'] = 'bookshare'
    emma_record['emma_repositoryMetadataUpdateDate'] = bks_record['lastUpdated']
    try:
        if exists(bks_record, 'site'):
            emma_record['emma_repository'] = BKS_SITE
            emma_record['emma_collection'] = [ bks_record['site'] ]
        if exists(bks_record, 'bookshareId'):
            emma_record['emma_repositoryRecordId'] = str(bks_record['bookshareId'])
            emma_record['emma_webPageLink'] = 'https://www.bookshare.org/browse/book/' + str(bks_record['bookshareId'])
        if exists(bks_record, 'title'):
            emma_record['dc_title'] = bks_record['title']
        if exists(bks_record, 'isbn13'):
            emma_record['dc_identifier'] = ['isbn:' + bks_record['isbn13']]
        if exists(bks_record, 'relatedIsbns'):
            emma_record['dc_relation'] = get_relation(bks_record)
        if exists(bks_record, 'contributors')  :
            emma_record['dc_creator'] = get_creator_display_names(bks_record)
        if exists(bks_record, 'categories')  :
            emma_record['dc_subject'] = get_categories(bks_record)
        if exists(bks_record, 'copyrightDate'):
            emma_record['dcterms_dateCopyright'] = bks_record['copyrightDate']
        if exists(bks_record, 'publisher'):
            emma_record['dc_publisher'] = bks_record['publisher']
        if exists(bks_record, 'usageRestriction'):
            emma_record['dc_rights'] = get_restriction(bks_record) 
        if exists(bks_record, 'publishDate'):
            emma_record['dcterms_dateAccepted'] = bks_record['publishDate'] 
        if 'languages' in bks_record and len(bks_record['languages']) > 0:
            emma_record['dc_language'] = bks_record['languages']
        return emma_record
    except Exception as e:
        logger.error("Exception thrown in get_title_field_record")
        logger.error(str(e))
        logger.error(bks_record)


def get_relation(bks_record):
    """
    Populate the Dublin Core relation element with related ISBNs
    """
    related_isbns = bks_record['relatedIsbns']
    if len(related_isbns) > 0:
        return list(map(lambda x: 'isbn:' + x, related_isbns))



def get_restriction(bks_record):
    """
    Translate Bookshare Usage Restriction to Dublin Core rights
    """
    restriction = bks_record['usageRestriction']['name'].replace(" ", "").lower()
    return BKS_RESTRICTION_TRANSLATION[restriction]


def get_creator_display_names(bks_record):
    """
    Use normalized Bookshare Display Name to create Dublin Core creator records
    """
    result = []
    if exists(bks_record, 'contributors') :
        for contributor in bks_record['contributors']:
            if contributor['type'] in ['author','editor']:
                if contributor['name']['displayName'] not in result:
                    result.append(contributor['name']['displayName'])    
    return result


def get_categories(bks_record):
    """
    Create simple list of category strings from Bookshare category list
    """
    result = []
    if exists(bks_record, 'categories'):
        for category in bks_record['categories']:
            result.append(category['name'])
    return result


def add_daisy_accessibility_features(daisy_record, artifact_map):
    """
    Add known accessibility features to Bookshare DAISY artifacts
    """
    daisy_record['s_accessibilityFeature'] = [
        'displayTransformability/font-size',
        'displayTransformability/color',
        'displayTransformability/background-color',
        'bookmarks',
        'readingOrder',
        'structuralNavigation'
    ]
    daisy_record['s_accessibilityControl'] = [
        'fullKeyboardControl', 'fullMouseControl']
    daisy_record['s_accessibilityHazard'] = [
        'noFlashingHazard', 'noMotionSimulationHazard', 'noSoundHazard']


def add_brf_accessibility_features(brf_record, artifact_map):
    """
    Add known accessibility features to Bookshare BRF artifacts
    """
    brf_record['s_accessibilityFeature'] = [
        'braille'
    ]
    format_feature_list = []
    if artifact_map is not None and exists(artifact_map, 'BRF'):
        artifact = artifact_map['BRF']
        if exists(artifact, 'brailleCode') and artifact['brailleCode'].upper() in ['UEB', 'EBAE']:
            format_feature_list.append(artifact['brailleCode'].lower())
        if exists(artifact, 'brailleGrade') and artifact['brailleGrade'].upper() in ['CONTRACTED', 'UNCONTRACTED']:
            if 'UNCONTRACTED' == artifact['brailleGrade'].upper():
                format_feature_list.append('grade1')
            else:
                format_feature_list.append('grade2')
        if exists(artifact, 'brailleMusicScoreLayout'):
            format_feature_list.append('music')
    else:
        if exists(brf_record, 'dc_language') and len(brf_record['dc_language']) > 0 and 'eng' in brf_record['dc_language']:
            format_feature_list.append('ueb')
            format_feature_list.append('ebae')
        format_feature_list.append('grade1')
        format_feature_list.append('grade2')

    brf_record['emma_formatFeature'] = format_feature_list


def add_daisy_audio_accessibility_features(daisy_audio_record, artifact_map, format):
    """
    Add known accessibility features to Bookshare BRF artifacts
    """
    daisy_audio_record['s_accessibilityFeature'] = [
        'sound'
    ]
    daisy_audio_record['s_accessMode'] = [
        'auditory'
    ]
    daisy_audio_record['s_accessModeSufficient'] = [
        'auditory'
    ]
    format_features = []

    if artifact_map is not None and exists(artifact_map, format):
        artifact = artifact_map[format]
        if exists(artifact, 'narrator'):
            narrator = artifact['narrator']
            if exists(narrator, 'type'):
                format_features.append(narrator['type'])
    else:
        format_features.append('tts')
    daisy_audio_record['emma_formatFeature'] = format_features



def add_textual_visual(emma_record):
    emma_record['s_accessMode'] = ['visual', 'textual']
    emma_record['s_accessModeSufficient'] = ['visual', 'textual']


def get_retrieval_link(bks_record, original_format):
    """
    Get the API retrieval link for the Bookshare artifact download. 
    """
    if exists(bks_record, 'links'):
        link_list = filter(lambda x: x['rel'] == 'download', bks_record['links'])
        link = list(link_list)[0]
        return link['href'].replace('{format}', original_format)
     

