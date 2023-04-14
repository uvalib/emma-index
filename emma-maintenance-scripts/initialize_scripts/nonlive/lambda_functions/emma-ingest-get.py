from shared.aws_util import get_aws_lambda_client

client = get_aws_lambda_client(profile_name='emma')

def create(env):
    s3key = 'emma-ingest-get-' + env + '.zip'

    client.create_function(
        FunctionName='emma-ingest-get-' + env,
        Runtime='python3.8',
        Role='{{REDACTED}}',
        Handler='recordGets.lambda_handler',
        Code={
            'S3Bucket': 'emma-lambda-initialize-function-code',
            'S3Key': s3key
        },
        Description='Put metadata records from API Endpoint calls into ElasticSearch',
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
                "EMMA_ELASTICSEARCH_INDEX": "emma-federated-index-alias-" + env,
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