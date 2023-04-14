import requests
import json
import os
from hathitrust_shared import config


def send_list(record_list, logger):
    emma_headers = {'x-api-key': config.EMMA_API_KEY}
    logger.info("Sending records to ingestion point")
    r = requests.put(os.environ.get('EMMA_INGESTION_URL', 'Missing'),
                     headers=emma_headers, json=record_list)
    if r.status_code == 202:
        logger.info("Ingestion success.")
    elif r.status_code == 207:
        logger.info(
            "Partial failure.  Status code: " + str(r.status_code) + "  Errors: " + str(
                r.text))
    else:
        logger.error("Ingestion returned failure: " +
                     str(r.status_code) + "  " + str(r.text))
        logger.info("Records")
        logger.info("\n" + json.dumps(record_list))