from shared.aws_util import get_aws_lambda_client

client = get_aws_lambda_client(profile_name='emma')


def create(env):
    s3key = 'hathitrust-get-file-' + env + '.zip'

    client.create_function(
        FunctionName='hathitrust-get-file-' + env,
        Runtime='python3.8',
        Role='{{REDACTED}}',
        Handler='get_hathi_file.lambda_handler',
        Code={
            'S3Bucket': 'emma-lambda-initialize-function-code',
            'S3Key': s3key
        },
        Description='Retrieve Hathitrust files from their website',
        Publish=True,
        Timeout=120,
        PackageType='Zip',
        Environment={
            'Variables': {
                "GOLDEN_KEY": env,
                "TARGET_BUCKET": "hathifiles-bigfiles-" + env,
                "DYNAMO_FILE_TABLE": "hathitrust_retrieval_" + env,
                "SOURCE_URL": "https://www.hathitrust.org/hathifiles"
            }
        },
        TracingConfig={
            'Mode': 'PassThrough'
        },
        Tags={
            'product': 'emma',
            'env': env,
            "GOLDEN_KEY": env,
            'codecommit': 'emma-hathitrust-processors'
        }
    )