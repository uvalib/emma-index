import logging
from lxml import html
import requests
import boto3
import json
import os
import re
from boto3.dynamodb.conditions import Key, Attr

"""
get_hathi_file.py
Downloads the oldest undownloaded differential update file from the HathiTrust files web page, and saves it in S3.
"""
logger = logging.getLogger()
logger.setLevel(logging.INFO)

DYNAMO_FILE_TABLE = os.environ.get('DYNAMO_FILE_TABLE', 'hathitrust_retrieval_qa')
TARGET_BUCKET = os.environ.get('TARGET_BUCKET', 'Missing')
OLDEST_DATE_TO_PROCESS = os.environ.get('OLDEST_DATE_TO_PROCESS', '20211101')
SOURCE_URL = os.environ.get('SOURCE_URL', 'https://www.hathitrust.org/hathifiles')
LINK_XPATH_SELECTOR = '//main//table//tr/td/a'
DIFF_FILE_PATTERN = r'hathi_upd_(\d{8}).txt.gz'
COMPLETE_STATUS = 'complete'
NAME_HASH = 'hathitrust'


def lambda_handler(event, context):
    """
    Set up the environment, then run the main function
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DYNAMO_FILE_TABLE)
    main(table, SOURCE_URL, TARGET_BUCKET)


def main(table, source_url, target_bucket):
    """
    It helps to have this separate from the main lambda function for testing
    """
    files_to_download = get_files_to_download(source_url)
    file_to_download = get_file_to_download(table, files_to_download)
    if file_to_download is not None:
        logger.info("Getting " + file_to_download + " from " + files_to_download[file_to_download])
        transfer_to_s3(files_to_download[file_to_download], file_to_download, target_bucket)
        record_processed_file(table, file_to_download, files_to_download[file_to_download])
    logger.info("Lambda function run complete.")


def transfer_to_s3(source_url, filename, target_bucket):
    """
    Based on: https://stackoverflow.com/a/42493144/809289
    By: GISD
    :param source_url:
    :param filename:
    :param target_bucket:
    :return:
    """
    logger.info("Writing to target bucket: " + target_bucket)
    s3 = boto3.resource('s3')
    request_image_stream = requests.get(source_url, stream=True)
    raw_image_stream = request_image_stream.raw
    image_data = raw_image_stream.read()
    s3.Bucket(target_bucket).put_object(Key='incoming/' + filename, Body=image_data)


def get_files_to_download(source_url):
    """
    Retrieve file list from external HathiTrust files page.
    Parse out list of differential update files.
    Throw away ones that are too old.
    """
    page = requests.get(source_url)
    tree = html.fromstring(page.content)
    links = tree.xpath(LINK_XPATH_SELECTOR)
    diff_files = {}
    for link in links:
        groups = re.match(DIFF_FILE_PATTERN, link.text)
        if groups is not None and len(groups.groups()) > 0 and groups.group(1) >= OLDEST_DATE_TO_PROCESS:
            diff_files[link.text.strip()] = link.get('href')
    return diff_files


def get_file_to_download(table, files_to_download):
    """
    Pick the oldest undownloaded file from the list.
    """
    filenames_set = files_to_download.keys()
    filenames_list = list(filenames_set)
    processed_file_list = get_processed_file_list(table, filenames_list[0])
    undownloaded = filenames_set - set(processed_file_list)
    if len(undownloaded) > 0:
        undownloaded_list = sorted(list(undownloaded))
        return undownloaded_list[0]

def get_processed_file_list(table, oldest_file):
    """
    Get the list of files that we've already downloaded from the database
    """
    file_date = get_date_from_file(oldest_file)
    result = []
    response = table.query(
        KeyConditionExpression=Key('name').eq(NAME_HASH) & Key('filedate').gte(file_date)
    )
    logger.debug('\n' + json.dumps(response,sort_keys=True, indent=4))
    items = response['Items']
    if items is not None:
        result = list(map(lambda i: i.get('filename'), items))
    return result


def get_date_from_file(filename):
    """
    Parse the 8-digit date out of the filename
    """
    groups = re.match(DIFF_FILE_PATTERN, filename)
    if groups is not None and len(groups.groups()) > 0:
        file_date = groups.group(1)
    else:
        file_date = "NO_DATE"
    logger.info("Extracted date from filename: " + file_date)
    return file_date


def record_processed_file(table, filename, url):
    """
    Once we've downloaded a file, record that fact in the database.
    To cope with the way DynamoDB works, the key 'name' is always the same.  file_date is an attribute we can compare and sort.
    """
    file_date = get_date_from_file(filename)
    table.put_item(
        Item={
            'name': NAME_HASH,
            'filename': filename,
            'filedate': file_date,
            'url': url,
            'status': COMPLETE_STATUS,
        }
    )