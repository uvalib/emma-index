#!/usr/bin/env python3

import boto3
import json
from time import sleep
from datetime import datetime

SOURCE_BUCKET = 'hathitrust-upload-qa'


def copy_s3_completed(s3_resource, source_bucket, source_key, old_key, new_key):
    copy_source = {
        'Bucket': source_bucket,
        'Key': source_key
    }
    target_key = source_key.replace(old_key, new_key)
    s3_resource.Object(source_bucket, target_key).copy_from(CopySource=copy_source)
    s3_resource.Object(source_bucket, source_key).delete()

def get_num_messages(sqs_client):
    response = sqs_client.get_queue_attributes(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/123456/incoming-metadata-to-process-qa',
        AttributeNames=['ApproximateNumberOfMessagesNotVisible']
    )
    num_messages = int(response['Attributes']['ApproximateNumberOfMessagesNotVisible'])
    return int(num_messages)

boto3.setup_default_session()
session = boto3.Session(profile_name='emma', region_name='us-east-1')
s3_client = session.client('s3')
s3_resource = boto3.resource('s3')
sqs_client = session.client('sqs')

# ApproximateNumberOfMessagesVisible


response = s3_client.list_objects(
    Bucket=SOURCE_BUCKET,
    Prefix='incoming/hathi_upd_2020'
)

older_than = datetime(2021, 10, 22)

contents = response['Contents']
count = 0
for item in contents:
    print("Item to refresh: " + item['Key'])
    last_modified = item['LastModified'].replace(tzinfo=None)
    print("Item last modified: " + str(last_modified))
    if last_modified < older_than:
        copy_s3_completed(s3_resource, SOURCE_BUCKET, item['Key'], 'incoming', 'redo')

        new_item = item['Key'].replace('incoming', 'redo')
        print(new_item)
        copy_s3_completed(s3_resource, SOURCE_BUCKET, new_item, 'redo', 'incoming')

        count = count + 1
        if count % 1000 == 0:
            print("Count: " + str(count))
        num_messages = get_num_messages(sqs_client)
        print("Number of messages: " + str(num_messages))

        while num_messages > 100 :
            sleep(60)
            num_messages = get_num_messages(sqs_client)



