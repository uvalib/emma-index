"""
hathitrust_retry.py
"touch" chunked HathiTrust files to regenerate the S3 CreateObject event that creates
SQS messages that drive hathitrust_scan
"""
import boto3
from datetime import datetime
from datetime import timedelta
from hathitrust_shared import config
from hathitrust_shared.s3_util import copy_s3_completed


def lambda_handler(event, context):
    """
    Top-level function that handles the incoming lambda event
    """
    boto3.setup_default_session()
    session = boto3.Session()
    s3_client = session.client('s3')
    s3_resource = boto3.resource('s3')
    sqs_client = session.client('sqs')

    older_than = get_yesterday()

    num_messages = get_num_messages(sqs_client)
    if num_messages < 200:
        response = s3_client.list_objects(
            Bucket=config.SOURCE_BUCKET,
            Prefix='incoming/',
            MaxKeys=100
        )
        if 'Contents' in response:
            contents = response['Contents']
            for item in contents:
                last_modified = item['LastModified'].replace(tzinfo=None)
                if last_modified < older_than:
                    new_item = item['Key'].replace('incoming', 'redo')
                    copy_s3_completed(s3_resource, config.SOURCE_BUCKET, item['Key'], 'incoming', 'redo')
                    print("Touching " + new_item)
                    copy_s3_completed(s3_resource, config.SOURCE_BUCKET, new_item, 'redo', 'incoming')


def get_num_messages(sqs_client):
    response = sqs_client.get_queue_attributes(
        QueueUrl=config.SQS_URL,
        AttributeNames=['ApproximateNumberOfMessagesNotVisible']
    )
    print("Checking " + config.SQS_URL)
    num_messages = int(response['Attributes']['ApproximateNumberOfMessagesNotVisible'])
    print("ApproximateNumberOfMessagesNotVisible: " + str(num_messages))
    return int(num_messages)


def get_yesterday():
    today = datetime.today()
    yesterday = today - timedelta(days=1)
    return yesterday



