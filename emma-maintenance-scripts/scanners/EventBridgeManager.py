import boto3
import json
from shared import config
from shared.aws_util import get_aws_lambda_client


class EventBridgeManager:
    """
    Enables and disables the connection between Eventbridge timers and the Lambda functions that they trigger.
    """

    INVOKER_SUFFIX = "-invoker"

    def __init__(self, env=config.GOLDEN_KEY, profile_name=config.AWS_PROFILE):
        self.env = env
        self.profile_name = profile_name
        self.client = self.__get_aws_eventbridge_client(profile_name)
        self.lambda_client = get_aws_lambda_client()

    def __get_aws_eventbridge_client(self, profile_name):
        """
        Get eventbridge client
        """
        boto3.setup_default_session()
        if profile_name is not None:
            session = boto3.Session(profile_name=profile_name,region_name=config.DEFAULT_REGION)
        else:
            session = boto3.Session()
        return session.client('events')

    def disable_ingest_eventbridge(self):
        responses = []
        for function_name in config.EVENTBRIDGE_SCAN_FUNCTION_RULE_MAP:
            full_function_name = function_name + '-' + self.env
            rule = self.__get_full_rule_name_from_function(function_name)
            target = self.__function_name_to_target(function_name)
            self.__revoke_eventbridge_permission(full_function_name)
            print(full_function_name)
            print(rule)
            response = self.client.remove_targets(Rule=rule, Ids=[full_function_name])
            responses.append(response)
            assert (not self.__target_exists_for_rule(rule, target))
        return responses

    def enable_ingest_eventbridge(self):
        responses = []
        for function_name in config.EVENTBRIDGE_SCAN_FUNCTION_RULE_MAP:
            full_function_name = function_name + '-' + self.env
            full_rule_name = self.__get_full_rule_name_from_function(function_name)
            target = self.__function_name_to_target(function_name)
            self.__grant_eventbridge_permission(full_function_name, full_rule_name)
            response = self.client.put_targets(Rule=full_rule_name, Targets=[ target ])
            responses.append(response)
            assert(self.__target_exists_for_rule(full_rule_name, target))
        return responses

    def verify(self, enabled):
        """
        Verify that the EventBridge triggers are enabled or disabled.
        """
        for function_name in config.EVENTBRIDGE_SCAN_FUNCTION_RULE_MAP:
            rule = self.__get_full_rule_name_from_function(function_name)
            target = self.__function_name_to_target(function_name)
            assert (self.__target_exists_for_rule(rule, target) == enabled)
            assert (self.__permission_exists(function_name) == enabled)

    def __permission_exists(self, function_name):
        """
        Check to see if an EventBridge timer has permission to trigger a specific Lambda function
        """
        permission_found = False
        full_function_name = function_name + '-' + self.env
        sid = full_function_name + self.INVOKER_SUFFIX
        try:
            policy = self.lambda_client.get_policy(FunctionName=full_function_name)
            if 'Policy' in policy:
                policy_object = json.loads(policy['Policy'])
                print(json.dumps(policy_object, indent=4))
                for statement in policy_object['Statement']:
                    if statement['Sid'] == sid:
                        permission_found = True
        except self.lambda_client.exceptions.ResourceNotFoundException as e:
            # This is an acceptable response; the permission does not exist.
            pass

        return permission_found


    def list_event_sources_for_function(self, function_name):
        """

        """
        full_function_name = function_name + '-' + self.env
        arn = config.LAMBDA_ARN_PREFIX + full_function_name
        return self.client.list_rule_names_by_target(TargetArn=arn, Limit=10)

    def __function_name_to_target(self, function_name):
        """

        """
        full_function_name = function_name + '-' + self.env
        arn = config.LAMBDA_ARN_PREFIX + full_function_name
        target = {
            'Id': full_function_name,
            'Arn': arn
        }
        return target

    def __get_full_rule_name_from_function(self, function_name):
        """

        """
        return 'emma-' + self.env + '-' + config.EVENTBRIDGE_SCAN_FUNCTION_RULE_MAP[function_name]

    def __target_exists_for_rule(self, rule_name, target):
        """

        """
        existing_targets = self.client.list_targets_by_rule(Rule=rule_name)
        target_found = False
        for existing_target in existing_targets['Targets']:
            print(json.dumps(existing_target))
            if existing_target['Arn'] == target['Arn']:
                target_found = True
                break
        return target_found

    def __grant_eventbridge_permission(self, function_name, rule):
        """
        Adds resource-based policy statement to Lambda function
        aws lambda add-permission \
            --function-name LogScheduledEvent \
            --statement-id my-scheduled-event \
            --action 'lambda:InvokeFunction' \
            --principal events.amazonaws.com \
            --source-arn {{REDACTED}}

        """
        rule_arn = config.EVENTBRIDGE_RULE_ARN_PREFIX + rule
        self.lambda_client.add_permission(
            FunctionName=function_name,
            StatementId=function_name + self.INVOKER_SUFFIX,
            Action='lambda:InvokeFunction',
            Principal='events.amazonaws.com',
            SourceArn=rule_arn
        )

    def __revoke_eventbridge_permission(self, function_name):
        """
        Removes resource-based policy statement from Lambda function
        aws lambda add-permission \
            --function-name LogScheduledEvent \
            --statement-id my-scheduled-event \
            --action 'lambda:InvokeFunction' \
            --principal events.amazonaws.com \
            --source-arn {{REDACTED}}

        """
        try:
            self.lambda_client.remove_permission(
                FunctionName=function_name,
                StatementId=function_name + self.INVOKER_SUFFIX
            )
        except self.lambda_client.exceptions.ResourceNotFoundException as e:
            # This is an acceptable response; the permission does not exist.
            print("The permission for %s was already removed." % function_name)

