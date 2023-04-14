from shared.aws_util import get_aws_lambda_client

client = get_aws_lambda_client(profile_name='emma')

def create(env):
    s3key = 'hathitrust-scan-' + env + '.zip'

    client.create_function(
        FunctionName='hathitrust-scan-' + env,
        Runtime='python3.8',
        Role='{{REDACTED}}',
        Handler='hathitrust_scan.hathitrust_scan.lambda_handler',
        Code={
            'S3Bucket': 'emma-lambda-initialize-function-code',
            'S3Key': s3key
        },
        Description='Process files from hathitrust-upload-' + env + '/incoming into the search index ingestion endpoint and move to staging',
        Publish=True,
        DeadLetterConfig={
            "TargetArn": "{{REDACTED}}" + env
        },
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