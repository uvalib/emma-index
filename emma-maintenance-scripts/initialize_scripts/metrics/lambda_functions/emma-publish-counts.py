from shared.aws_util import get_aws_lambda_client

client = get_aws_lambda_client(profile_name='emma')

def create(env):
    s3key = 'emma-publish-counts-' + env + '.zip'

    client.create_function(
        FunctionName='emma-publish-counts-' + env,
        Runtime='python3.8',
        Role='{{REDACTED}}',
        Handler='publish.publish_counts.lambda_handler',
        Code={
            'S3Bucket': 'emma-lambda-initialize-function-code',
            'S3Key': s3key
        },
        Description='Retrieve ElasticSearch document counts',
        Publish=True,
        Timeout=120,
        PackageType='Zip',
        VpcConfig={
            'SubnetIds': [
                "{{REDACTED}}"
            ],
            'SecurityGroupIds': [
                "{{REDACTED}}"
            ],
            "VpcId": "{{REDACTED-}}"
        },
        Environment={
            'Variables': {
                "ES_HOST_QA": "vpc-emma-{{REDACTED}}.es.amazonaws.com",
                "ES_INDEX_DEV": "emma-federated-index-alias-dev",
                "ES_HOST_DEV": "vpc-emma-{{REDACTED}}.es.amazonaws.com",
                "ES_INDEX_QA": "emma-federated-index-alias-qa",
                "ES_INDEX_STAGING": "emma-federated-index-alias-staging",
                "ES_HOST_STAGING": "vpc-emma{{REDACTED}}.es.amazonaws.com"
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