from shared.aws_util import get_aws_lambda_client
from initialize_scripts.live import config

def create(env):
    s3key = 'emma-maintenance-message-' + env + '.zip'
    client = get_aws_lambda_client(profile_name='emmalive')

    client.create_function(
        FunctionName='emma-maintenance-message-' + env,
        Runtime='python3.8',
        Role='{{REDACTED}}',
        Handler='maintenance.lambda_handler',
        Code={
            'S3Bucket': 'emma-prod-lambda-initialize-function-code',
            'S3Key': s3key
        },
        Description='Appropriate message and error code if the EMMA web service is down',
        Publish=True,
        VpcConfig=config.VPC_CONFIG,
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