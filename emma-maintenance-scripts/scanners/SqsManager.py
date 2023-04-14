from shared import config
from shared.aws_util import get_lambda_arn, get_queue_arn, get_aws_lambda_client
from time import sleep


class SqsManager:
    RETRIES = 5
    """

    A lambda function calling this will need the following policy

        {
                "Sid": "DevelopEventSourceMappings",
                "Effect": "Allow",
                "Action": [
                    "lambda:DeleteEventSourceMapping",
                    "lambda:UpdateEventSourceMapping",
                    "lambda:CreateEventSourceMapping"
                ],
                "Resource": "*",
                "Condition": {
                    "StringLike": {
                        "lambda:FunctionArn": "arn:aws:lambda:*:*:function:intern-*"
                    }
                }
            },
    """

    def __init__(self, env=config.GOLDEN_KEY):
        self.env = env
        self.lambda_client = get_aws_lambda_client()

    def disable_ingest_sqs(self):
        return self.__update_sqs_mapping(False)

    def enable_ingest_sqs(self):
        return self.__update_sqs_mapping(True)

    def verify(self, enabled):
        for function_name in config.SQS_SCAN_FUNCTION_MAP:
            queue_name = config.SQS_SCAN_FUNCTION_MAP[function_name]
            mappings = self.__list_event_source_mappings(function_name, queue_name)
            mapping_state = mappings["EventSourceMappings"][0]["State"]
            print("%s to %s mapping is %s" % (queue_name, function_name, mapping_state))
            if enabled:
                assert mapping_state in ['Enabling', 'Enabled', 'Updating']
            else:
                assert mapping_state in ['Disabling', 'Disabled', 'Updating']

    def __update_sqs_mapping(self, enabled):
        responses = []
        for function_name in config.SQS_SCAN_FUNCTION_MAP:
            for attempt in range(self.RETRIES):
                queue_name = config.SQS_SCAN_FUNCTION_MAP[function_name]
                mappings = self.__list_event_source_mappings(function_name, queue_name)
                uuid = mappings["EventSourceMappings"][0]["UUID"]
                try:
                    response = self.lambda_client.update_event_source_mapping(UUID=uuid, Enabled=enabled)
                    break
                except self.lambda_client.exceptions.ResourceInUseException as e:
                    print("Updating %s to %s mapping had ResourceInUseException, retrying..." % (
                    queue_name, function_name))
                    sleep(10)
            responses.append(response)
        return responses

    def __list_event_source_mappings(self, function_name, queue_name):
        function_arn = get_lambda_arn(function_name, self.env)
        queue_arn = get_queue_arn(queue_name, self.env)
        return self.lambda_client.list_event_source_mappings(FunctionName=function_arn, EventSourceArn=queue_arn)
