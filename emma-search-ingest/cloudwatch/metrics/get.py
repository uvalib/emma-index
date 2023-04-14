import boto3
import logging
import json
import os
import requests

from datetime import datetime, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    endpoint = os.environ.get('API_ENDPOINT', None)

    response = requests.get(endpoint)
    json_object = response.json()
    stats = json_object['stats']

    cloudwatch = boto3.client('cloudwatch')

    for env in stats.keys():
        env_stats = stats[env]
        for repo in env_stats.keys():
            count = env_stats[repo]
            metric_data = [
                {
                    'MetricName': 'doc_count',
                    'Dimensions': [
                        {
                            'Name': 'EMMA_SERVICE',
                            'Value': 'ElasticSearch'
                        },
                        {
                            'Name': 'ENVIRONMENT',
                            'Value': env
                        },
                        {
                            'Name': 'REPOSITORY',
                            'Value': repo
                        },
                    ],
                    'Unit': 'None',
                    'Timestamp': datetime.now(timezone.utc),
                    'Value': count
                },
            ]
            print(env + ' ' + repo + ' ' + str(count))
            response = cloudwatch.put_metric_data(
                MetricData=metric_data,
                Namespace='emma-federated-search'
            )
    print ("Lambda function call completed.")


