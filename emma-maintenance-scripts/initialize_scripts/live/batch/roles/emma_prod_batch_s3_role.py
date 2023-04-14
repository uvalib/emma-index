from shared.aws_util import get_aws_session


def create(env):
    client = get_aws_session(profile_name='emmalive').client('iam')
    role_name = 'emma_' + env + '_batch_s3_role'
    client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument='''{
                "Version": "2012-10-17",
                "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ecs-tasks.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }        ''',
        Description='Allows ECS tasks to call AWS services on your behalf.',
        Tags=[
            {'Key': 'product', "Value": 'emma'},
            {'Key': 'env', "Value": env},
            {'Key': 'GOLDEN_KEY', "Value": env}
        ]
    )

    client.attach_role_policy(
        RoleName=role_name,
        PolicyArn='{{REDACTED-ARN}}'
    )
    client.attach_role_policy(
        RoleName=role_name,
        PolicyArn='{{REDACTED-ARN}}'
    )
