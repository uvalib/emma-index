import json
from shared.aws_util import get_aws_session

def create(env):
    client = get_aws_session(profile_name='emmalive').client('iam')
    ac_client = get_aws_session(profile_name='emmalive').client('accessanalyzer')

    policy_document = '''{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "allowFullBatchAccess",
            "Effect": "Allow",
            "Action": "batch:*",
            "Resource": "*"
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
        PolicyName='emma_' + env + '_allow_full_batch_access',
        PolicyDocument=policy_document,
        Description='Allow trigger of AWS Batch jobs on your behalf',
        Tags= [
            {'Key': 'product', "Value": 'emma'},
            {'Key': 'env', "Value": env},
            {'Key': 'GOLDEN_KEY', "Value": env}
        ]
    )
