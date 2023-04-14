import boto3
from shared import config
from datetime import datetime
import json


def get_aws_lambda_client(profile_name=config.AWS_PROFILE):
    """
    Get lambda client
    """
    session = get_aws_session(profile_name)
    return session.client('lambda')

def get_aws_cloudwatch_client(profile_name=config.AWS_PROFILE, region_name=config.DEFAULT_REGION):
    """
    Get Cloudwatch client
    """
    session = get_aws_session(profile_name, region_name)
    return session.client('cloudwatch')


def get_apigateway_client(profile_name=config.AWS_PROFILE, region_name=config.DEFAULT_REGION):
    """
    Get API Gateway client
    """
    session = get_aws_session(profile_name, region_name)
    return session.client('apigateway')


def get_dynamo_client(profile_name=config.AWS_PROFILE, region_name=config.DEFAULT_REGION):
    """
    Get Dynamo DB client
    """
    session = get_aws_session(profile_name, region_name)
    return session.client('dynamodb')


def get_sts_client(profile_name=config.AWS_PROFILE, region_name=config.DEFAULT_REGION):
    """
    Get STS (roles and identities) client
    """
    session = get_aws_session(profile_name, region_name)
    return session.client('sts')


def get_aws_session(profile_name=config.AWS_PROFILE, region_name=config.DEFAULT_REGION):
    boto3.setup_default_session()
    if profile_name is not None:
        session = boto3.Session(profile_name=profile_name, region_name=region_name)
    else:
        session = boto3.Session()
    return session


def get_lambda_arn(function_name, env=config.GOLDEN_KEY):
    full_function_name = function_name + '-' + env
    arn = config.LAMBDA_ARN_PREFIX + full_function_name
    return arn


def get_queue_arn(queue_name, env=config.GOLDEN_KEY):
    full_queue_name = queue_name + '-' + env
    queue_arn = config.SQS_ARN_PREFIX + full_queue_name
    return queue_arn


def fix_dates_aws_for_json(response):
    """
    So far dates appear to be only at the top level, so we won't go through the entire tree
    """
    if isinstance(response, dict):
        for key in response:
            if isinstance(response[key], datetime):
                response[key] = response[key].isoformat()
            if isinstance(response[key], dict) or isinstance(response[key], list) :
                response[key] = fix_dates_aws_for_json(response[key])
    if isinstance(response, list):
        new_response = [item.isoformat() if isinstance(item, datetime) else item for item in response]
        new_response = [fix_dates_aws_for_json(item) if isinstance(item, dict) or isinstance(item, list) else item for item in new_response]
        response = new_response

    return response


def grant_api_gateway_invokes_lambda_permissions(api_id, api_name, http_method, path, env):
    """
    This needs to be run when the maintenance function is first created so the API gateway can invoke it.
    """
    # aws lambda add-permission   \
    # > --function-name "emma-maintenance-message-dev"   \
    # > --source-arn "{{REDACTED}}"   \
    # > --principal apigateway.amazonaws.com   \
    # > --statement-id "invokeMaintenanceFunction"   \
    # > --action lambda:InvokeFunction \
    # > --profile emma
    source_arn = config.LAMBDA_EXECUTE_PERMISSION_PREFIX + ":" + api_id + "/*/" + http_method + path
    function_name = config.API_MAINTENANCE_LAMBDA_FUNCTION_NAME + "-" + env
    cleanPath =  re.sub(r'[^a-zA-Z0-9]', '', path)

    statement_id = 'invokeMaintenanceFunction' + api_name.capitalize() + http_method.capitalize() + cleanPath.capitalize()
    client = get_aws_lambda_client()
    try:
        response = client.add_permission(
            FunctionName=function_name,
            StatementId=statement_id,
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=source_arn
        )
        print(json.dumps(response, sort_keys=True, indent=4))
    except:
        pass