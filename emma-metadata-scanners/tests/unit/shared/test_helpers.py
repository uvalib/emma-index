import boto3
import logging
from moto import mock_dynamodb2
from shared import dynamo


logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
        KeySchema=[
            {
                "AttributeName": "name",
                "KeyType": "HASH"
            }
        ],
        AttributeDefinitions=[
            {
                "AttributeName": "name",
                "AttributeType": "S"
            }
        ],
        ProvisionedThroughput={
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5
        }
    )
    return table

def print_dynamo_value(table, name):
    result = dynamo.get_db_value(table, name)
    if result is not None:
        logger.info(name + ": " + str(result))
    else:
        logger.info(name + ": None")