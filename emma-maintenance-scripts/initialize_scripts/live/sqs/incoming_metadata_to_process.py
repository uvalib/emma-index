
from shared.aws_util import get_aws_session

def create(env):
    client = get_aws_session(profile_name='emmalive').client('sqs')
    client.create_queue(
        QueueName='incoming-metadata-to-process-' + env,
        # Attributes={
        #     'string': 'string'
        # },
        tags={
            'product': 'emma',
            'env': env,
            "GOLDEN_KEY": env,
            'codecommit': 'emma-hathitrust-processors'
        }
    )