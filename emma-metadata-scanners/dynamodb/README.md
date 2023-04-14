To create a new DynamoDB Table of the format used by these lambda functions, update the table name in create_dev_dynamo.json.

Then run:

` aws dynamodb create-table --profile emma --cli-input-json file://create_dev_dynamo.json`

emma is a nickname for the role that allows editing of EMMA code.

Make sure you have an up-to-date version of the AWS CLI installed.