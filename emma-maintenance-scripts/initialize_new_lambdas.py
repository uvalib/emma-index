from shared.aws_util import get_aws_lambda_client

client = get_aws_lambda_client(profile_name='emma')

envs = ['qa', 'staging', 'dev']
for env in envs:
    s3key = 'hathitrust-retry-' + env + '.zip'
    print(s3key)
    client.create_function(
        FunctionName='hathitrust-retry-' + env,
        Runtime='python3.9',
        Role='{{REDACTED}}',
        Handler='hathitrust_retry.hathitrust_retry.lambda_handler',
        Code={
            'S3Bucket': 'emma-lambda-hathitrust-retry-function-code',
            'S3Key': s3key
        },
        Description='Retrigger files that have not been processed in S3 bucket hathitrust-upload-' + env + '/incoming',
        Publish=True,
        # VpcConfig={
        #     'SubnetIds': [
        #         "{{REDACTED}}"
        #     ],
        #     'SecurityGroupIds': [
        #         "{{REDACTED}}"
        #     ]
        # },
        Timeout=900,
        PackageType='Zip',
        Environment={
            'Variables': {
                "GOLDEN_KEY": env,
                "SQS_URL": 'https://sqs.us-east-1.amazonaws.com/{{REDACTED}}-' + env,
                "SOURCE_BUCKET": "hathitrust-upload-" + env
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
