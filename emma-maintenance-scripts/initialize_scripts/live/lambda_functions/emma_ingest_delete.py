from shared.aws_util import get_aws_lambda_client
from initialize_scripts.live import config

def create(env):
    s3key = 'emma-ingest-delete-' + env + '.zip'
    client = get_aws_lambda_client(profile_name='emmalive')

    client.create_function(
        FunctionName='emma-ingest-delete-' + env,
        Runtime='python3.8',
        Role='{{REDACTED}}',
        Handler='recordDeletes.lambda_handler',
        Code={
            'S3Bucket': 'emma-prod-lambda-initialize-function-code',
            'S3Key': s3key
        },
        Description='Delete records from ElasticSearch',
        Publish=True,
        VpcConfig=config.VPC_CONFIG,
        Timeout=120,
        PackageType='Zip',
        Environment={
            'Variables': {
                "GOLDEN_KEY": env,
                "EMMA_ELASTICSEARCH_INDEX": "emma-federated-index-alias-" + env,
                "EMMA_ELASTICSEARCH_HOST": config.ELASTICSEARCH_HOST
            }
        },
        TracingConfig={
            'Mode': 'PassThrough'
        },
        Tags={
            'product': 'emma',
            'env': env,
            "GOLDEN_KEY": env,
            'codecommit': 'emma-search-ingest'
        }
    )