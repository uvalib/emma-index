from snapshots import snapshot

host = "https://vpc-emma-{{REDACTED}}.es.amazonaws.com/"
role_arn = "{{REDACTED}}"
snapshot_repository = "emma-federated-index-nonlive-backup"
s3_bucket_name = "emma-nonlive-test-snapshot-bucket"
index = "restored-emma-federated-index-qa-1.0.1"
taken_because = "test"

snapshot.delete_index(host=host,
                      index=index)
