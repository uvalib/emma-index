from shared.aws_util import get_aws_lambda_client

client = get_aws_lambda_client(profile_name='emma')

def create(env):
    s3key = 'hathitrust-batch-trigger-' + env + '.zip'

    client.create_function(
        FunctionName='hathitrust-batch-trigger-' + env,
        Runtime='python3.8',
        Role='{{REDACTED}}',
        Handler='batch_trigger.lambda_handler',
        Code={
            'S3Bucket': 'emma-lambda-initialize-function-code',
            'S3Key': s3key
        },
        Description='Trigger the HathiTrust file chunking batch job',
        Publish=True,
        Timeout=300,
        PackageType='Zip',
        Environment={
            'Variables': {
                "TARGET_BUCKET": "hathitrust-upload-" + env,
                "JOB_QUEUE": "emma-hathitrust-bigfiles-queue-" + env,
                "JOB_DEFINITION": "emma-bigfiles-" + env + ":6",
                "LINES_PER_FILE": "500",
                "JOB_NAME": "launch_hathitrust_chunkinator_" + env
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