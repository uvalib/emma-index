#!/usr/bin/env python3

import boto3
from time import sleep
from datetime import datetime
import re

"""
This script was used to fix an issue where all of the "full" chunked hathitrust files were dumped into the root
of an S3 bucket, making them difficult to browse and manage.
"""
SOURCE_BUCKET = 'hathitrust-upload-qa'


def copy_s3_completed(s3_resource, source_bucket, source_key, old_key, new_key):
    copy_source = {
        'Bucket': source_bucket,
        'Key': source_key
    }
    target_key = source_key.replace(old_key, new_key)
    s3_resource.Object(source_bucket, target_key).copy_from(CopySource=copy_source)
    s3_resource.Object(source_bucket, source_key).delete()


def get_prefix_string(source_key):
    """
    Extract the date from the filename and turn it into a S3 prefix
    """
    date_extract_pattern=r'-chunk-000(?P<tt>\d)(?P<thou>\d)(?P<hun>\d)(?P<tens>\d)(?P<ones>\d).txt'
    date_string = ''
    match = re.search(date_extract_pattern, source_key)
    if match:
        match_dict = match.groupdict()
        date_string = '000' + match_dict['tt'] + '/' + match_dict['thou'] + '/' + match_dict['hun']
    return date_string

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


boto3.setup_default_session()
session = boto3.Session(profile_name='emma', region_name='us-east-1')
s3_client = session.client('s3')
s3_resource = boto3.resource('s3')

# hathi_full_20200401-chunk-00002499.txt
response = s3_client.list_objects(
    Bucket=SOURCE_BUCKET,
    Prefix='completed/hathi_full'
)


while 'Contents' in response:
    contents = response['Contents']
    for item in contents:
        print("Item to move: "+ SOURCE_BUCKET + " " + item['Key'])
        new_prefix = 'completed' + get_date_string_as_prefix(item['Key']) + '/' + get_prefix_string(item['Key'])
        copy_s3_completed(s3_resource, SOURCE_BUCKET, item['Key'], 'completed', new_prefix)

    response = s3_client.list_objects(
        Bucket=SOURCE_BUCKET,
        Prefix='completed/hathi_full'
    )





