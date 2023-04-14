"""
Run from project root as
nohup pipenv run python -m hathitrust_loader.batch dev &
Where dev is environment name (like GOLDEN_KEY in Bookshare)
"""
import logging
import csv
import sys
import os

from hathitrust_shared import metadata, metadata_constants, record_handling, config


BATCH_SIZE = 100
FILE_NAME = 'data_files/hathi_full_20200101.txt'
ENV_NAME = 'dev'
INGESTION_URLS = {
    'dev' : '{{REDACTED}}'
}
SKIP_LINES = 0

if len(sys.argv) > 2:
    SKIP_LINES = int(sys.argv[2])

if len(sys.argv) > 1:
    ENV_NAME = sys.argv[1]

os.environ['EMMA_INGESTION_URL'] = INGESTION_URLS[ENV_NAME]

LOG_NAME = 'hathi_batch_'+ ENV_NAME + '_full.log'

logging.basicConfig(level=logging.INFO, filename=LOG_NAME, format='%(asctime)s %(levelname)s:%(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def load_file(file_name):
    with open(file_name, newline = '') as data_file:
        record_reader = csv.DictReader(data_file, delimiter='\t', fieldnames=metadata_constants.FIELD_NAMES, quoting=csv.QUOTE_NONE)
        count = 0
        total_count = 0
        record_list = []
        for line in record_reader:
            total_count = total_count + 1
            if total_count > SKIP_LINES:
                if metadata.ingestible_record(line) :
                    result = metadata.transform_record(line)
                    assert len(result['emma_repositoryRecordId']) > 0
                    assert result['emma_repository'] == 'hathiTrust'
                    assert result['dc_format'] == 'pdf'
                    record_list.append(result)
                    count = count + 1
                    if count % BATCH_SIZE == 0:
                        record_handling.send_list(record_list, logger)
                        record_list = []
                        logger.info("Processed " + str(count) + " lines, total including skipped " + str(total_count))

    logger.info("Processed " + str(count) + " lines, total including skipped " + str(total_count))
    if record_list is not None and len(record_list) > 0:
        record_handling.send_list(record_list, logger)
        logger.info("Processed " + str(count) + " lines, total including skipped " + str(total_count))
    logger.info("Lambda call complete.")

