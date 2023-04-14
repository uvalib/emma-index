import json
from shared.aws_util import get_aws_session

def create(env):
    client = get_aws_session(profile_name='emmalive').client('iam')
    ac_client = get_aws_session(profile_name='emmalive').client('accessanalyzer')

    policy_document = '''{
    "Version": "2012-10-17",
    "Statement": [
{
                    "Sid": "allowUpdateTargets",
                    "Effect": "Allow",
                    "Action": [
                        "events:PutTargets",
                        "events:RemoveTargets"
                    ],
                    "Resource": "{{REDACTED}}"
                },
                {
                    "Sid": "allowListTargets",
                    "Effect": "Allow",
                    "Action": [
                        "events:ListRules",
                        "events:ListRuleNamesByTarget",
                        "events:ListTargetsByRule"
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
        PolicyName='emma_' + env + '_allow_add_remove_eventbridge_targets',
        PolicyDocument=policy_document,
        Description='Allow addition and removal of Lambda functions as Eventbridge targets',
        Tags= [
            {'Key': 'product', "Value": 'emma'},
            {'Key': 'env', "Value": env},
            {'Key': 'GOLDEN_KEY', "Value": env}
        ]
    )
