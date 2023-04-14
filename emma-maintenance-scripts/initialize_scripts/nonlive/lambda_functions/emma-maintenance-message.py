from shared.aws_util import get_aws_lambda_client

client = get_aws_lambda_client(profile_name='emma')

def create(env):
    s3key = 'emma-maintenance-message-' + env + '.zip'

    client.create_function(
        FunctionName='emma-maintenance-message-' + env,
        Runtime='python3.8',
        Role='{{REDACTED}}',
        Handler='maintenance.lambda_handler',
        Code={
            'S3Bucket': 'emma-lambda-initialize-function-code',
            'S3Key': s3key
        },
        Description='Appropriate message and error code if the EMMA web service is down',
        Publish=True,
        VpcConfig={
            'SubnetIds': [
                "{{REDACTED}}"
            ],
            'SecurityGroupIds': [
                "{{REDACTED}}"
            ],
            "VpcId": "{{REDACTED}}"
        },
        Timeout=10,
        PackageType='Zip',
        Environment={
            'Variables': {
                "GOLDEN_KEY": env,
            }
        },
        TracingConfig={
            'Mode': 'PassThrough'
        },
        Tags={
            'product': 'emma',
            'env': env,
            "GOLDEN_KEY": env,
            'codecommit': 'emma-search-ingest'
        }
    )