import boto3
import botocore.session
from botocore.stub import Stubber

from batch_trigger import lambda_handler
from unittest.mock import MagicMock, patch


@patch.object(boto3, "client")
def test_do_nothing_smoke_test(mock_client):
    stubbed_client = botocore.session.get_session().create_client('batch')
    stubber = Stubber(stubbed_client)
    stubber.add_response('submit_job', sample_batch_response)
    stubber.activate()
    mock_client.return_value = stubbed_client
    lambda_handler(sample_s3_event_json, None)


sample_batch_response = {
    "ResponseMetadata": {
        "RequestId": "3efe1ad0-e6c9-4b17-af61-9342458ed2ca",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
            "date": "Wed, 03 Nov 2021 20:26:02 GMT",
            "content-type": "application/json",
            "content-length": "203",
            "connection": "keep-alive",
            "x-amzn-requestid": "3efe1ad0-e6c9-4b17-af61-9342458ed2ca",
            "access-control-allow-origin": "*",
            "x-amz-apigw-id": "IPp-GHDZoAMFcVA=",
            "access-control-expose-headers": "X-amzn-errortype,X-amzn-requestid,X-amzn-errormessage,X-amzn-trace-id,X-amz-apigw-id,date",
            "x-amzn-trace-id": "Root=1-6182f05a-33cd5e1025f711f03d04b0e0"
        },
        "RetryAttempts": 0
    },
    "jobArn": "{{REDACTED}}",
    "jobName": "launch_hathitrust_chunkinator_prod_hathi_upd_20200413",
    "jobId": "f7dd025a-7110-4cd3-ac8a-4dfef33e997e"
}

"""
Sample event from AWS Documentation
https://docs.aws.amazon.com/lambda/latest/dg/with-s3-example.html
"""
sample_s3_event_json = {
  "Records": [
    {
      "eventVersion": "2.0",
      "eventSource": "aws:s3",
      "awsRegion": "us-west-2",
      "eventTime": "1970-01-01T00:00:00.000Z",
      "eventName": "ObjectCreated:Put",
      "userIdentity": {
        "principalId": "EXAMPLE"
      },
      "requestParameters": {
        "sourceIPAddress": "127.0.0.1"
      },
      "responseElements": {
        "x-amz-request-id": "EXAMPLE123456789",
        "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH"
      },
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "testConfigRule",
        "bucket": {
          "name": "my-s3-bucket",
          "ownerIdentity": {
            "principalId": "EXAMPLE"
          },
          "arn": "arn:aws:s3:::example-bucket"
        },
        "object": {
          "key": "HappyFace.jpg",
          "size": 1024,
          "eTag": "0123456789abcdef0123456789abcdef",
          "sequencer": "0A1B2C3D4E5F678901"
        }
      }
    }
  ]
}
