from shared.aws_util import get_aws_lambda_client

client = get_aws_lambda_client(profile_name='emma')

def create(env):
    s3key = 'emma-cloudwatch-metrics-' + env + '.zip'

    client.create_function(
        FunctionName='emma-cloudwatch-metrics-' + env,
        Runtime='python3.8',
        Role='{{REDACTED}}',
        Handler='metrics.get.lambda_handler',
        Code={
            'S3Bucket': 'emma-lambda-initialize-function-code',
            'S3Key': s3key
        },
        Description='Retrieve emma cloudwatch metrics',
        Publish=True,
        Timeout=120,
        PackageType='Zip',
        Environment={
            'Variables': {
                "GOLDEN_KEY": env,
                "API_ENDPOINT": "https://api." + env + ".bookshareunifiedsearch.org/totals"
            }
        },
        TracingConfig={
            'Mode': 'PassThrough'
        },
        Tags={
            'product': 'emma',
            'env': env,
            "GOLDEN_KEY": env
        }
    )