import csv
import gzip
import io
import sys
import re
from hathitrust_shared import config, metadata, record_handling, metadata_constants
from hathitrust_shared.s3_util import copy_s3_completed


def run(s3, source_bucket, source_key, logger):
    response = get_response(s3, source_bucket, source_key, logger)
    if response is not None:
        gzipped = gzip.GzipFile(None, 'rb', fileobj=response['Body'])
        data = io.TextIOWrapper(gzipped)
        csv.field_size_limit(sys.maxsize)
        record_reader = csv.DictReader(data, delimiter='\t', fieldnames=metadata_constants.FIELD_NAMES,
                                       quoting=csv.QUOTE_NONE)
        count = 0
        total_count = 0
        record_list = []
        logger.info('Processing file s3://' + str(source_bucket) + '/' + str(source_key))
        for line in record_reader:
            total_count = total_count + 1
            if metadata.ingestible_record(line):
                result = metadata.transform_record(line)
                assert len(result['emma_repositoryRecordId']) > 0
                assert result['emma_repository'] == 'hathiTrust'
                assert result['dc_format'] == 'pdf'
                record_list.append(result)
                count = count + 1
                if count % config.BKS_RECORD_LIST_SIZE == 0:
                    record_handling.send_list(record_list, logger)
                    record_list = []
                    logger.info("Processed " + str(count) + " lines, total including skipped " + str(total_count))
        if record_list is not None and len(record_list) > 0:
            record_handling.send_list(record_list, logger)
            logger.info("Processed " + str(count) + " lines, total including skipped " + str(total_count))
        copy_s3_completed(s3, source_bucket, source_key, to_prefix='completed' + get_date_string_as_prefix(source_key))
    logger.info("Lambda call complete.")


def get_date_string_as_prefix(source_key):
    """
    Extract the date from the filename and turn it into a S3 prefix
    """
    date_extract_pattern=r'_(?P<year>\d{4,4})(?P<month>\d{2,2})(?P<day>\d{2,2})'
    date_string = ''
    match = re.search(date_extract_pattern, source_key)
    if match:
        match_dict = match.groupdict()
        date_string = '/' + match_dict['year'] + '/' + match_dict['month'] + '/' + match_dict['day']
    return date_string


def get_response(s3, source_bucket, source_key, logger):
    """
    We have to handle the SQS promise of getting each message at least once--
    but possibly more than once.
    If the key doesn't exist, it's probably already been moved to completed.
    """
    response = None
    try:
        response = s3.Object(source_bucket, source_key).get()
    except s3.meta.client.exceptions.NoSuchKey:
        logger.info('No such key as ' + source_key + ', probably already processed')
    return response




