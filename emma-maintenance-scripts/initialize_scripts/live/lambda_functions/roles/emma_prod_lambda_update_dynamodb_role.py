from shared.aws_util import get_aws_session


def create(env):
    client = get_aws_session(profile_name='emmalive').client('iam')
    role_name = 'emma_' + env + '_lambda_update_dynamodb_role'
    client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument='''{
                "Version": "2012-10-17",
                "Statement":
        [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]}
        ''',
        Description='Allows Lambda functions to call DynamoDB and write to Cloudwatch on your behalf.',
        Tags=[
            {'Key': 'product', "Value": 'emma'},
            {'Key': 'env', "Value": env},
            {'Key': 'GOLDEN_KEY', "Value": env}
        ]
    )

    client.attach_role_policy(
        RoleName=role_name,
        PolicyArn='{{REDACTED}}'
    )
    client.attach_role_policy(
        RoleName=role_name,
        PolicyArn='{{REDACTED}}'
    )
