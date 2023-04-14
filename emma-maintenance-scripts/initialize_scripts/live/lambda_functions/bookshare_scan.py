from shared.aws_util import get_aws_lambda_client


def create(env):
    s3key = 'bookshare-scan-' + env + '.zip'
    client = get_aws_lambda_client(profile_name='emmalive')

    client.create_function(
        FunctionName='bookshare-scan-' + env,
        Runtime='python3.8',
        Role='{{REDACTED}}',
        Handler='bookshare_scan.bookshare_scan.lambda_handler',
        Code={
            'S3Bucket': 'emma-prod-lambda-initialize-function-code',
            'S3Key': s3key
        },
        Description='Scan the Bookshare V2 API and load entries into the API Ingestion Endpoint',
        Publish=True,
        Timeout=300,
        PackageType='Zip',
        Environment={
            'Variables': {
                "X_BOOKSHARE_ORIGIN": "bksema00",
                "BKS_API_PASSWORD": "{{REDACTED}}",
                "EMMA_INGESTION_URL": "https://ingest." + env + ".bookshareunifiedsearch.org/records/",
                "BKS_API_USERNAME": "{{REDACTED}}",
                "EMMA_STATUS_TABLE_NAME": "emma_bookshare_loader_" + env,
                "BKS_API_KEY": "{{REDACTED}}",
                "BKS_SITE": "bookshare",
                "EMMA_STATUS_TABLE_PREFIX": "BKS_",
                "BKS_API_BASE_URL": "https://api.bookshare.org/v2",
                "GOLDEN_KEY": env,
                "BKS_API_TOKEN_URL": "https://auth.bookshare.org/oauth/token",
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