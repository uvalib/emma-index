from shared import config
from snapshots import snapshot

host = "https://vpc-{{REDACTED}}.es.amazonaws.com/"
role_arn = "{{REDACTED}}"
snapshot_repository = "emma-federated-index-staging-backup"
s3_bucket_name = "emma-staging-migration-snapshot-bucket"
indices = "emma-federated-index-staging-1.0.1"


host = "https://vpc-{{REDACTED}}.es.amazonaws.com/"
role_arn = "{{REDACTED}}"
snapshot_repository = "emma-federated-index-nonlive-backup"
s3_bucket_name = "emma-nonlive-test-snapshot-bucket"
indices = "emma-federated-index-qa-1.0.1"

role_arn = "{{REDACTED}}"
snapshot_repository = "emma-federated-index-staging-backup"
s3_bucket_name = "emma-staging-migration-snapshot-bucket"
indices = "emma-federated-index-staging-1.0.1"


snapshot_name="snapshot-emma-federated-index-staging-1.0.1-2021-09-15-19-23-02"


snapshot.restore_snapshot(host=host,
                          snapshot_repository=snapshot_repository,
                          snapshot_name=snapshot_name,
                          indices=indices)
