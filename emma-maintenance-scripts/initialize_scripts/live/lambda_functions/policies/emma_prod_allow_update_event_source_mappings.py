import json
from shared.aws_util import get_aws_session

def create(env):
    client = get_aws_session(profile_name='emmalive').client('iam')
    ac_client = get_aws_session(profile_name='emmalive').client('accessanalyzer')

    policy_document = '''{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "manageLambda",
            "Effect": "Allow",
            "Action": [
                "lambda:AddPermission",
                "lambda:RemovePermission"
            ],
            "Resource": "{{REDACTED}}"
        },
        {
            "Sid": "updateEventSourceMapping",
            "Effect": "Allow",
            "Action": [
                "lambda:UpdateEventSourceMapping"
            ],
            "Resource": "{{REDACTED}}"
        },
        {
            "Sid": "getPolicy",
            "Effect": "Allow",
            "Action": [
                "lambda:GetPolicy"
            ],
            "Resource": "{{REDACTED}}"
        },
        {
            "Sid": "viewLambda",
            "Effect": "Allow",
            "Action": [
                "lambda:ListEventSourceMappings"
            ],
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
        PolicyName='emma_' + env + '_allow_update_event_source_mappings',
        PolicyDocument=policy_document,
        Description='Allow updating of API Gateway endpoint target Lambda functions',
        Tags= [
            {'Key': 'product', "Value": 'emma'},
            {'Key': 'env', "Value": env},
            {'Key': 'GOLDEN_KEY', "Value": env}
        ]
    )
