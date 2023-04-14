from shared.aws_util import get_aws_lambda_client

client = get_aws_lambda_client(profile_name='emma')

# I don't think that this function is currently working or being used

def create(env):
    s3key = 'emma-federated-search-es-count-' + env + '.zip'

    client.create_function(
        FunctionName='emma-federated-search-es-count-' + env,
        Runtime='python3.8',
        Role='{{REDACTED}}',
        Handler='get_passthrough.lambda_handler',
        Code={
            'S3Bucket': 'emma-lambda-initialize-function-code',
            'S3Key': s3key
        },
        Description='Send a search query from the API endpoint to the Elasticsearch server',
        Publish=True,
        VpcConfig={
            'SubnetIds': [
                "{{REDACTED}}"
            ],
            'SecurityGroupIds': [
                "{{REDACTED}}"
            ],
            "VpcId": "{{REDACTED}}"
        },
        Timeout=120,
        PackageType='Zip',
        Environment={
            'Variables': {
                "GOLDEN_KEY": env,
                "EMMA_ELASTICSEARCH_TYPE": "count",
                "EMMA_ELASTICSEARCH_HOST": "vpc-emma-{{REDACTED}}.es.amazonaws.com"
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