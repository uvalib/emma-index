"""
batch_trigger.py
Launches batch jobs for incoming files in S3
"""
import logging
import boto3
import json
import os
import re

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TARGET_BUCKET = os.environ.get('TARGET_BUCKET', 'Missing')
LINES_PER_FILE = os.environ.get('LINES_PER_FILE', '500')
JOB_NAME = os.environ.get('JOB_NAME', 'Missing')
JOB_QUEUE = os.environ.get('JOB_QUEUE', 'Missing')
JOB_DEFINITION = os.environ.get('JOB_DEFINITION', 'Missing')

def lambda_handler(event, context):
    """
    Top-level function that handles the incoming lambda event
    """
    # We know the following has a table.
    # pylint: disable=maybe-no-member
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logging.info("Triggering event: " + json.dumps(event))

    batch = boto3.client('batch')

    source_bucket = event['Records'][0]['s3']['bucket']['name']
    source_key = event['Records'][0]['s3']['object']['key']
    logger.info("source_key " + source_key)
    path, basename = os.path.split(source_key)
    basename = basename.split(".", maxsplit=1)[0]
    basename = re.sub(r'[^A-Za-z0-9_\-]', '_', basename)
    job_name = JOB_NAME + "_" + basename
    command_args = [source_bucket, source_key, TARGET_BUCKET,  "incoming/" + basename, LINES_PER_FILE]

    logger.info("Submitting job name " + job_name + " definition " + JOB_DEFINITION + " to queue " + JOB_QUEUE)

    logger.info("Command arguments: " + str(command_args))
    batch_response = batch.submit_job(jobName=job_name,
                                jobQueue=JOB_QUEUE,
                                jobDefinition=JOB_DEFINITION,
                                containerOverrides={
                                    "command": command_args
                                })

    logger.info(json.dumps(batch_response))
    logger.info("End of batch submission")





