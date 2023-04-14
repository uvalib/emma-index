import boto3
import requests
from shared import config
import json
from requests_aws4auth import AWS4Auth


headers = {"Content-Type": "application/json"}


def get_aws_es_credentials(profile_name=config.AWS_PROFILE):
    """
    Get AWS credentials necessary to perform snapshot
    """
    service = 'es'
    boto3.setup_default_session()
    if profile_name is not None:
        session = boto3.Session(profile_name=profile_name)
    else:
        session = boto3.Session()
    credentials = session.get_credentials()
    print(session.profile_name)
    print(credentials.access_key)
    return AWS4Auth(credentials.access_key, credentials.secret_key, config.DEFAULT_REGION, service,
                    session_token=credentials.token)


def register_snapshot_repository(host, role_arn, snapshot_repository, s3_bucket_name, readonly=True,
                                 region=config.DEFAULT_REGION):
    """
    Register snapshot repository
    """
    payload = {
      "type": "s3",
      "settings": {
        "bucket": s3_bucket_name,
        "region": region,
        "role_arn": role_arn,
        "readonly": readonly
      }
    }
    path = '_snapshot/' + snapshot_repository  # the Elasticsearch API endpoint
    url = host + path
    print("Connecting to " + url)
    r = requests.put(url, auth=get_aws_es_credentials(), json=payload, headers=headers)
    print(r.status_code)
    print(r.text)
    return r


def take_snapshot(host, indices, snapshot_repository, snapshot_name, taken_by, taken_because):
    """
    Take snapshot
    host:
    """
    payload = {}
    if indices:
      payload["indices"] = indices
    if taken_by or taken_because:
      payload["metadata"] = {}
      if taken_by:
        payload["metadata"]["taken_by"] =  taken_by
      if taken_because:
        payload["metadata"]["taken_because"] = taken_because

    path = '_snapshot/' + snapshot_repository + '/' + snapshot_name
    url = host + path

    r = requests.put(url, auth=get_aws_es_credentials(), json=payload, headers=headers)
    print(r.status_code)
    print(r.text)
    return r


def delete_index(host, index):
    """
    Delete index
    """
    url = host + index
    r = requests.delete(url, auth=get_aws_es_credentials())
    print(r.status_code)
    print(r.text)
    return r


def restore_snapshot(host, snapshot_repository, snapshot_name, indices="-.kibana*,-.tasks"):
    """
    Restore snapshot (all indices except Kibana and fine-grained access control)
    """
    path = '_snapshot/' + snapshot_repository + '/' +snapshot_name + '/_restore'
    url = host + path
    payload = {
      "indices": indices,
      "include_global_state": False
    }
    r = requests.post(url, auth=get_aws_es_credentials(), json=payload, headers=headers)
    print(r.status_code)
    print(r.text)
    return r


def test_restore_snapshot(host, snapshot_repository, snapshot_name, indices="-.kibana*,-.tasks"):
    """
    Restore snapshot (all indices except Kibana and fine-grained access control)
    """
    path = '_snapshot/' + snapshot_repository + '/' +snapshot_name + '/_restore'
    url = host + path
    payload = {
        "indices": indices,
        "include_global_state": False,
        "rename_pattern": "emma-federated-index-(.+)",
        "rename_replacement": "restored-emma-federated-index-$1",
        "include_aliases": False
    }
    print(json.dumps(payload,indent=4))
    r = requests.post(url, auth=get_aws_es_credentials(), json=payload, headers=headers)
    print(r.status_code)
    print(r.text)
    return r

