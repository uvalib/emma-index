import logging
import boto3
from moto import mock_dynamodb2
import json
from unittest.mock import patch
from get_hathi_file import get_files_to_download, record_processed_file, get_processed_file_list, main

BUCKET_NAME = "bogus_bucket"
TABLE_NAME = "bogus_table"
SOURCE_URL = 'https://www.hathitrust.org/hathifiles'

@mock_dynamodb2
def test_get_empty_dynamo_db():
    # Set up the data
    table = create_dynamo_table(TABLE_NAME)
    # Run the test
    processed_file_list = get_processed_file_list(table, "hathi_upd_20200330.txt.gz")
    # Check the results
    assert len(processed_file_list) == 0

@mock_dynamodb2
def test_get_processed_file_list():
    # Set up the data
    table = create_dynamo_table(TABLE_NAME)
    record_processed_file(table, 'hathi_upd_20200401.txt.gz', 'https://www.hathitrust.org/filebrowser/download/292090')
    record_processed_file(table, 'hathi_upd_20200402.txt.gz', 'https://www.hathitrust.org/filebrowser/download/292094')
    # Run the test
    processed_file_list = get_processed_file_list(table, "hathi_upd_20200330.txt.gz")
    # Check the results
    assert len(processed_file_list) == 2


@mock_dynamodb2
@patch('get_hathi_file.transfer_to_s3')
@patch('get_hathi_file.get_files_to_download')
def test_main(mock_get_files_to_download, mock_transfer_to_s3):
    # Set up the data
    mock_get_files_to_download.return_value = get_sample_hathi_list()
    table = create_dynamo_table(TABLE_NAME)
    record_processed_file(table, 'hathi_upd_20200401.txt.gz', 'https://www.hathitrust.org/filebrowser/download/292090')
    # Run the test
    main(table, SOURCE_URL, BUCKET_NAME)
    # Check the results
    processed_file_list = get_processed_file_list(table, "hathi_upd_20200330.txt.gz")
    print(processed_file_list)
    assert len(processed_file_list) == 2
    assert processed_file_list == ['hathi_upd_20200401.txt.gz', 'hathi_upd_20200402.txt.gz']


@mock_dynamodb2
@patch('get_hathi_file.transfer_to_s3')
@patch('get_hathi_file.get_files_to_download')
def test_multiple_main(mock_get_files_to_download, mock_transfer_to_s3):
    # Set up the data
    mock_get_files_to_download.return_value = get_sample_hathi_list()
    table = create_dynamo_table(TABLE_NAME)
    record_processed_file(table, 'hathi_upd_20200401.txt.gz', 'https://www.hathitrust.org/filebrowser/download/292090')
    # Run the test
    for count in range(10):
        main(table, SOURCE_URL, BUCKET_NAME)
    # Check the results
    processed_file_list = get_processed_file_list(table, "hathi_upd_20200330.txt.gz")
    assert len(processed_file_list) == 10
    assert processed_file_list == ['hathi_upd_20200401.txt.gz', 'hathi_upd_20200402.txt.gz', 'hathi_upd_20200403.txt.gz', 'hathi_upd_20200404.txt.gz', 'hathi_upd_20200405.txt.gz', 'hathi_upd_20200406.txt.gz', 'hathi_upd_20200407.txt.gz', 'hathi_upd_20200408.txt.gz', 'hathi_upd_20200409.txt.gz', 'hathi_upd_20200410.txt.gz']


@mock_dynamodb2
@patch('get_hathi_file.transfer_to_s3')
@patch('get_hathi_file.get_files_to_download')
def test_main_empty_table(mock_get_files_to_download, mock_transfer_to_s3):
    # Set up the data
    mock_get_files_to_download.return_value = get_sample_hathi_list()
    table = create_dynamo_table(TABLE_NAME)
    # Run the test
    main(table, SOURCE_URL, BUCKET_NAME)
    # Check the results
    processed_file_list = get_processed_file_list(table, "hathi_upd_20200330.txt.gz")
    assert len(processed_file_list) == 1
    assert processed_file_list == ['hathi_upd_20200401.txt.gz']

def get_sample_hathi_list() :
    return {
      'hathi_upd_20200401.txt.gz': 'https://www.hathitrust.org/filebrowser/download/292090',
      'hathi_upd_20200402.txt.gz': 'https://www.hathitrust.org/filebrowser/download/292094',
      'hathi_upd_20200403.txt.gz': 'https://www.hathitrust.org/filebrowser/download/292096',
      'hathi_upd_20200404.txt.gz': 'https://www.hathitrust.org/filebrowser/download/292097',
      'hathi_upd_20200405.txt.gz': 'https://www.hathitrust.org/filebrowser/download/292098',
      'hathi_upd_20200406.txt.gz': 'https://www.hathitrust.org/filebrowser/download/292102',
      'hathi_upd_20200407.txt.gz': 'https://www.hathitrust.org/filebrowser/download/292156',
      'hathi_upd_20200408.txt.gz': 'https://www.hathitrust.org/filebrowser/download/292158',
      'hathi_upd_20200409.txt.gz': 'https://www.hathitrust.org/filebrowser/download/292159',
      'hathi_upd_20200410.txt.gz': 'https://www.hathitrust.org/filebrowser/download/292160'
    }


@mock_dynamodb2
def create_dynamo_table(table_name):
    # Create a mock table
    dynamodb = boto3.resource('dynamodb', 'us-east-1')

    # Derived from
    # aws dynamodb describe-table --table-name emma_bookshare_loader --profile emma
    # We know the following has create_table.
    # pylint: disable=maybe-no-member
    table = dynamodb.create_table(
        TableName=table_name,
        AttributeDefinitions=[
            {
                "AttributeName": "name",
                "AttributeType": "S"
            },
            {
                "AttributeName": "filedate",
                "AttributeType": "S"
            },
        ],
        KeySchema=[
            {
                "AttributeName": "name",
                "KeyType": "HASH"
            },
            {
                "AttributeName": "filedate",
                "KeyType": "RANGE"
            }
        ],

        ProvisionedThroughput={
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5
        }
    )
    return table