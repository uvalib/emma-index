# Batch trigger AWS Lambda Function

This is a lambda function which kicks off chunkinator script on AWS Batch.

It is triggered by a new file being added to a "big file" S3 bucket.

## Example config information 

This is a configuration information dump as the result of a lambda function update command.

```shell script
aws lambda update-function-code --profile emma --function-name hathitrust-batch-trigger-qa --zip-file fileb://deploy/hathitrust-batch-trigger-qa.zip
```

```json
{
    "FunctionName": "hathitrust-batch-trigger-qa",
    "FunctionArn": "{{REDACTED}}",
    "Runtime": "python3.7",
    "Role": "{{REDACTED}}",
    "Handler": "batch_trigger.lambda_handler",
    "CodeSize": 939,
    "Description": "",
    "Timeout": 60,
    "MemorySize": 128,
    "LastModified": "2020-04-15T19:43:21.865+0000",
    "CodeSha256": "2B3H7fdfXhkqVvdFmK6+/B6fMGiJYTW72O4tn/5V9vI=",
    "Version": "$LATEST",
    "VpcConfig": {
        "SubnetIds": [],
        "SecurityGroupIds": [],
        "VpcId": ""
    },
    "Environment": {
        "Variables": {
            "TARGET_BUCKET": "hathitrust-upload-qa",
            "JOB_QUEUE": "emma-hathitrust-bigfiles-queue-qa",
            "JOB_DEFINITION": "emma-bigfiles-qa:3",
            "LINES_PER_FILE": "500",
            "JOB_NAME": "launch_hathitrust_chunkinator_qa"
        }
    },
    "TracingConfig": {
        "Mode": "PassThrough"
    },
    "RevisionId": "490fb32a-70c2-4712-ae82-f073b9c5c1e7",
    "State": "Active",
    "LastUpdateStatus": "Successful"
}