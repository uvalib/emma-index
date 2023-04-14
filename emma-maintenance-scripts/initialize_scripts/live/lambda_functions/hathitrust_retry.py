from shared.aws_util import get_aws_lambda_client


def create(env):
    s3key = 'hathitrust-retry-' + env + '.zip'
    client = get_aws_lambda_client(profile_name='emmalive')

    client.create_function(
        FunctionName='hathitrust-retry-' + env,
        Runtime='python3.8',
        Role='{{REDACTED}}',
        Handler='hathitrust_retry.hathitrust_retry.lambda_handler',
        Code={
            'S3Bucket': 'emma-prod-lambda-initialize-function-code',
            'S3Key': s3key
        },
        Description='Retrigger files that have not been processed in S3 bucket hathitrust-upload-' + env + '/incoming',
        Publish=True,
        Timeout=300,
        PackageType='Zip',
        Environment={
            'Variables': {
                "GOLDEN_KEY": env,
                "SOURCE_BUCKET": "hathitrust-upload-" + env,
                "SQS_URL": "https://sqs.us-east-1.amazonaws.com/123456789/incoming-metadata-to-process-" + env
            }
        },
        TracingConfig={
            'Mode': 'PassThrough'
        },
        Tags={
            'product': 'emma',
            'env': env,
            "GOLDEN_KEY": env,
            'codecommit': 'emma-metadata-scanners'
        }
    )