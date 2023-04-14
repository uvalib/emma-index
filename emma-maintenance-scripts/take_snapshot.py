from shared import config
from snapshots import snapshot
import datetime

now = datetime.datetime.now()
taken_by = "Caden Howell"

host = "https://vpc-emma{{REDACTED}}.es.amazonaws.com/"
role_arn = "{{REDACTED}}"
snapshot_repository = "emma-federated-index-nonlive-backup"
s3_bucket_name = "emma-nonlive-test-snapshot-bucket"
indices = "emma-federated-index-qa-1.0.1"
taken_because = "test"

host = "https://vpc-{{REDACTED}}.es.amazonaws.com/"
role_arn = "{{REDACTED}}"
snapshot_repository = "emma-federated-index-staging-backup"
s3_bucket_name = "emma-staging-migration-snapshot-bucket"
indices = "emma-federated-index-staging-1.0.1"






snapshot_name = "snapshot-" + indices + "-" + now.strftime("%Y-%m-%d-%H-%M-%S")

snapshot.take_snapshot(host=host,
                       indices=indices,
                       snapshot_repository=snapshot_repository,
                       snapshot_name=snapshot_name,
                       taken_by=taken_by,
                       taken_because=taken_because)
