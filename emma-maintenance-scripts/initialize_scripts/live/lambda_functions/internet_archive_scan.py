from shared.aws_util import get_aws_lambda_client


def create(env):
    s3key = 'internet-archive-scan-' + env + '.zip'
    client = get_aws_lambda_client(profile_name='emmalive')

    client.create_function(
        FunctionName='internet-archive-scan-' + env,
        Runtime='python3.8',
        Role='{{REDACTED}}',
        Handler='lambda_function.lambda_handler',
        Code={
            'S3Bucket': 'emma-prod-lambda-initialize-function-code',
            'S3Key': s3key
        },
        Description='Scan the internet archive scrap endpoint and load entries into the API Ingestion Endpoint',
        Publish=True,
        Timeout=300,
        PackageType='Zip',
        Environment={
            'Variables': {
                "GOLDEN_KEY": env,
                "EMMA_INGESTION_URL": "https://ingest.staging.bookshareunifiedsearch.org/records/",
                "EMMA_API_KEY": "{{REDACTED}}"
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