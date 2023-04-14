from shared import config
from snapshots import snapshot

host = "https://vpc-emma-{{REDACTED}}.es.amazonaws.com/"
role_arn = "{{REDACTED}}"
snapshot_repository = "emma-federated-index-nonlive-backup"
s3_bucket_name = "emma-nonlive-test-snapshot-bucket"

host = "https://vpc-{{REDACTED}}.es.amazonaws.com/"
role_arn = "{{REDACTED}}"
snapshot_repository = "emma-federated-index-staging-backup"
s3_bucket_name = "emma-staging-migration-snapshot-bucket"






snapshot.register_snapshot_repository(host=host,
                                      role_arn=role_arn,
                                      snapshot_repository=snapshot_repository,
                                      s3_bucket_name=s3_bucket_name,
                                      readonly=False
                                      )
