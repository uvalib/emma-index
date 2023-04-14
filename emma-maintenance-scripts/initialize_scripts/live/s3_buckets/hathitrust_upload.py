
from shared.aws_util import get_aws_session

def create(env):
    # Need to add "Block all public access"
    client = get_aws_session(profile_name='emmalive').client('s3')
    client.create_bucket(
        ACL='private',
        Bucket='hathitrust-upload-' + env
    )