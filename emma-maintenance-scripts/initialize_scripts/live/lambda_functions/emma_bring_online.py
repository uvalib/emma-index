from shared.aws_util import get_aws_lambda_client


def create(env):
    s3key = 'emma-bring-online-' + env + '.zip'
    client = get_aws_lambda_client(profile_name='emmalive')
    client.create_function(
        FunctionName='emma-bring-online-' + env,
        Runtime='python3.8',
        Role='{{REDACTED}}',
        Handler='take_offline.lambda_handler',
        Code={
            'S3Bucket': 'emma-prod-lambda-initialize-function-code',
            'S3Key': s3key
        },
        Description='Bring the EMMA environment online',
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