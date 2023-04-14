from shared import config
from shared.aws_util import get_apigateway_client, get_lambda_arn, fix_dates_aws_for_json
import json
from time import sleep
import requests
"""
A lambda function calling this will need the following trust policy in an AWS service for API Gateway type role. 
https://docs.aws.amazon.com/apigateway/latest/developerguide/permissions.html


Or use resource-based policy like Eventbridge(?)
"""
class ApiGatewayManager:

    '''
    Data for looking up function name and verifying whether the enable/disable operation is successful
    '''
    API_ENDPOINT_TO_LAMBDA_FUNCTION_MAP = {
        "/recordDeletes": {
            "function_name": "emma-ingest-delete",
            "server_name": "ingest",
            "api_key": config.INGEST_API_KEY,
            "method": 'POST'},
        "/recordGets": {
            "function_name": "emma-ingest-get",
            "server_name": "ingest",
            "api_key": config.INGEST_API_KEY,
            "method": "POST"},
        "/records": {
            "function_name": "emma-ingest-put",
            "server_name": "ingest",
            "api_key": config.INGEST_API_KEY,
            "method": "PUT"},
        "/search": {"function_name": "emma-search-get",
            "server_name": "api",
            "api_key": config.INGEST_API_KEY,
            "method": "GET"}
    }

    API_ENDPOINT_DOMAIN = "bookshareunifiedsearch.org"

    API_MAINTENANCE_LAMBDA_FUNCTION_NAME = "emma-maintenance-message"

    API_GATEWAY_ID_MAP = {
        'qa': {'ingestion': '{{REDACTED}}', 'search': '{{REDACTED}}'},
        'staging': {'ingestion': '{{REDACTED}}', 'search': '{{REDACTED}}'},
        'dev': {'ingestion': '{{REDACTED}}', 'search': '{{REDACTED}}'}
    }

    def __init__(self, env=config.GOLDEN_KEY):
        self.env = env
        self.api_gateway_client = get_apigateway_client()

    def disable_ingest_api(self):
        return self.set_lambda_target(self.get_maintenance_target)

    def enable_ingest_api(self):
        return self.set_lambda_target(self.get_online_target)

    def get_maintenance_target(self, path):
        lambda_arn = get_lambda_arn(self.API_MAINTENANCE_LAMBDA_FUNCTION_NAME)
        return config.LAMBDA_INTEGRATION_PREFIX + lambda_arn + config.LAMBDA_INTEGRATION_SUFFIX

    def get_online_target(self, path):
        function_name = self.API_ENDPOINT_TO_LAMBDA_FUNCTION_MAP[path]['function_name']
        lambda_arn = get_lambda_arn(function_name, self.env)
        return config.LAMBDA_INTEGRATION_PREFIX + lambda_arn + config.LAMBDA_INTEGRATION_SUFFIX

    def verify(self, enabled):
        for path in self.API_ENDPOINT_TO_LAMBDA_FUNCTION_MAP:
            lambda_info = self.API_ENDPOINT_TO_LAMBDA_FUNCTION_MAP[path]
            server_name = lambda_info['server_name'] + '.' + self.env + '.' + self.API_ENDPOINT_DOMAIN
            url = "https://" + server_name + path
            method = lambda_info["method"]
            if 'api_key' in lambda_info:
                emma_headers = {'x-api-key': lambda_info['api_key']}
                r = requests.request(method=method, url=url, headers=emma_headers)
                print(r.text)
                if enabled:
                    if lambda_info['server_name'] == 'api':
                        assert ("Please include at least" in r.text)
                    else:
                        assert('Body is empty' in r.text)
                else:
                    assert("unavailable for maintenance" in r.text)

    def set_lambda_target(self, get_target_uri):
        responses = []

        api_id_map = self.API_GATEWAY_ID_MAP[self.env]
        for api_name in api_id_map:
            api_id = api_id_map[api_name]
            resources = self.api_gateway_client.get_resources(restApiId=api_id)
            print(json.dumps(resources, sort_keys=True, indent=4))
            for resource in resources['items']:
                resource_id = resource['id']
                path = resource['path']
                if 'resourceMethods' in resource and path != '/':
                    uri = get_target_uri(path)
                    for http_method in resource['resourceMethods']:
                        response = self.api_gateway_client.update_integration(
                            restApiId=api_id,
                            resourceId=resource_id,
                            httpMethod=http_method,
                            patchOperations=[
                                {
                                    'op': 'replace',
                                    'path': '/uri',
                                    'value': uri
                                },
                            ]
                        )
                        print(json.dumps(response, sort_keys=True, indent=4))
                        responses.append(response)
            '''
            AWS limit on create_deployment calls: 1 request every 5 seconds per account
            '''
            sleep(6)
            response = self.api_gateway_client.create_deployment(
                restApiId=api_id,
                stageName=self.env,
                description='Updating target to ' + uri
            )
            print(json.dumps(fix_dates_aws_for_json(response), sort_keys=True, indent=4))
            responses.append(response)
        return responses



