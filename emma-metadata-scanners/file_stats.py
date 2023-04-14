"""
Run from project root as
nohup pipenv run python -m hathitrust_loader.batch dev &
Where dev is environment name (like GOLDEN_KEY in Bookshare)
"""
import logging
import csv
import json
import sys

from hathitrust_shared import metadata, metadata_constants, config
from shared.EmmaValidator import EmmaValidator



if len(sys.argv) > 1:
    FILE_NAME = sys.argv[1]



LOG_NAME = 'hathi_batch_file_stat.log'

logging.basicConfig(level=logging.INFO, filename=LOG_NAME, format='%(asctime)s %(levelname)s:%(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

INGESTION_SCHEMA_FILE = 'shared/ingestion-record.schema.json'

emmaValidator = EmmaValidator(INGESTION_SCHEMA_FILE)
csv.field_size_limit(sys.maxsize)


def load_file(file_name):
    with open(file_name, newline = '', encoding="utf-8") as data_file:
        record_reader = csv.DictReader(data_file, delimiter='\t', fieldnames=metadata_constants.FIELD_NAMES)
        line_count = 0
        good_count = 0
        no_ingest_count = 0
        error_count = 0
        for line in record_reader:
            line_count = line_count + 1
            if metadata.ingestible_record(line) :
                result = metadata.transform_record(line)
                logger.info(json.dumps(result))
                assert len(result['emma_repositoryRecordId']) > 0
                assert result['emma_repository'] == 'hathiTrust'
                assert result['dc_format'] == 'pdf'

                errors = {}
                emmaValidator.validate(result, result['emma_repositoryRecordId'], errors)
                if len(errors) > 0:
                    logger.error("Validation errors " + str(errors))
                    error_count = error_count + 1
                else:
                    good_count = good_count + 1
            else:
                no_ingest_count = no_ingest_count + 1

    logger.info("Results: ")
    logger.info("Number of lines: " + str(line_count))
    logger.info("Number of validation error records: " + str(error_count))
    logger.info("Number of valid ingestible lines: " + str(good_count))
    logger.info("Number not ingestible: " + str(no_ingest_count))
    logger.info("Total of 3 counts: " + str(error_count+ good_count + no_ingest_count))


load_file(FILE_NAME)