from shared.aws_util import get_dynamo_client


def create(env):
    client = get_dynamo_client(profile_name='emmalive')
    client.create_table(
        AttributeDefinitions=[
            {
                "AttributeName": "name",
                "AttributeType": "S"
            }
        ],
        TableName="emma_bookshare_loader_" + env,
        KeySchema=[
            {
                "AttributeName": "name",
                "KeyType": "HASH"
            }
        ],
        # ProvisionedThroughput= {
        #     "ReadCapacityUnits": 5,
        #     "WriteCapacityUnits": 5
        # },
        Tags=[
            {'Key': 'product', "Value": 'emma'},
            {'Key': 'env', "Value": env},
            {'Key': 'GOLDEN_KEY', "Value": env},
            {'Key': 'codecommit', "Value": 'emma-metadata-scanners'}
        ],
        BillingMode="PAY_PER_REQUEST"
    )
