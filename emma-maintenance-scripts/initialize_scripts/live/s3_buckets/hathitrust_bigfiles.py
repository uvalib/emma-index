
from shared.aws_util import get_aws_session
# Need to add "Block all public access"
def create(env):
    client = get_aws_session(profile_name='emmalive').client('s3')
    client.create_bucket(
        ACL='private',
        Bucket='hathitrust-bigfiles-' + env
    )