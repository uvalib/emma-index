from shared.aws_util import get_aws_lambda_client
from initialize_scripts.live import config

def create(env):
    s3key = 'emma-publish-counts-' + env + '.zip'
    client = get_aws_lambda_client(profile_name='emmalive')

    client.create_function(
        FunctionName='emma-publish-counts-' + env,
        Runtime='python3.8',
        Role='{{REDACTED}}',
        Handler='publish.publish_counts.lambda_handler',
        Code={
            'S3Bucket': 'emma-prod-lambda-initialize-function-code',
            'S3Key': s3key
        },
        Description='Retrieve ElasticSearch document counts',
        Publish=True,
        Timeout=120,
        PackageType='Zip',
        VpcConfig=config.VPC_CONFIG,
        Environment={
            'Variables': {
                "ES_HOST_PROD": config.ELASTICSEARCH_HOST,
                "ES_INDEX_PROD": "emma-federated-index-alias-prod"
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