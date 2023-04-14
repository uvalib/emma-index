import json
from shared.aws_util import get_aws_session

def create(env):
    client = get_aws_session(profile_name='emmalive').client('iam')
    ac_client = get_aws_session(profile_name='emmalive').client('accessanalyzer')

    policy_document = '''{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "updateDynamoDbData",
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:DeleteItem",
                "dynamodb:Scan",
                "dynamodb:Query",
                "dynamodb:UpdateItem",
                "dynamodb:DescribeStream",
                "dynamodb:ListStreams",
                "dynamodb:DescribeTable",
                "dynamodb:GetShardIterator",
                "dynamodb:GetItem",
                "dynamodb:GetRecords"
            ],
            "Resource": [
                "{{REDACTED}}"
            ]
        }
    ]
}
        '''

    response = ac_client.validate_policy(
        policyDocument=policy_document,
        policyType='IDENTITY_POLICY'
    )
    print(json.dumps(response, indent=4))
    client.create_policy(
        PolicyName='emma_' + env + '_allow_update_dynamodb_tables',
        PolicyDocument=policy_document,
        Description='Allow updating of DynamoDB table data',
        Tags= [
            {'Key': 'product', "Value": 'emma'},
            {'Key': 'env', "Value": env},
            {'Key': 'GOLDEN_KEY', "Value": env}
        ]
    )
