from shared.aws_util import get_aws_lambda_client

client = get_aws_lambda_client(profile_name='emma')

def create(env):
    s3key = 'emma-take-offline-' + env + '.zip'

    client.create_function(
        FunctionName='emma-take-offline-' + env,
        Runtime='python3.8',
        Role='{{REDACTED}}',
        Handler='take_offline.lambda_handler',
        Code={
            'S3Bucket': 'emma-lambda-initialize-function-code',
            'S3Key': s3key
        },
        Description='Take the EMMA environment offline for maintenance',
        Publish=True,
        Timeout=600,
        PackageType='Zip',
        Environment={
            'Variables': {
                "GOLDEN_KEY": env
            }
        },
        TracingConfig={
            'Mode': 'PassThrough'
        },
        Tags={
            'product': 'emma',
            'env': env,
            "GOLDEN_KEY": env,
            'codecommit': 'emma-maintenance-scripts'
        }
    )