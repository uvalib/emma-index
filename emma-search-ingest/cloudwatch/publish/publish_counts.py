import boto3
import logging
import json
from publish import config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):

    response = {}
    stats = {}
    repository_list = ['bookshare', 'internetArchive', 'hathiTrust']
    for env in config.ES_CONFIGS.keys():
        env_stats = {}
        conf = config.ES_CONFIGS[env]
        es_conn = conf['conn']
        for repo in repository_list:
            count = es_conn.count(index=conf['index'], q='emma_repository:' + repo)
            env_stats[repo] = count['count']
            logger.info(json.dumps(response))
        stats[env] = env_stats
    response['stats'] = stats
    body = json.dumps(response, sort_keys=True, indent=4)
    logger.info(body)
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": body
    }



