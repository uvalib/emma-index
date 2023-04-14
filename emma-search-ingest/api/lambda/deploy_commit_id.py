#!/usr/bin/env python3
import sys
import os
import deploy_helpers

# Set parameter defaults
commit_id = "help"
env_param = "qa"
target_param = "all"

if len(sys.argv) > 3:
    target_param = sys.argv[3]
if len(sys.argv) > 2:
    env_param = sys.argv[2]
if len(sys.argv) > 1:
    commit_id = sys.argv[1]

if os.getenv('CODEBUILD_RESOLVED_SOURCE_VERSION'):
    # We're in CodeBuild
    PROFILE_PARAM = ""
else:
    # We're logged in as a person
    PROFILE_PARAM = " --profile emma "

S3_CODE_BUCKET_NAME = 'emma-search-ingest-deploy-packages'

TARGET_LIST = ['ingestion', 'search', 'maintenance']
ENV_LIST = ['dev', 'qa', 'staging', 'int', 'prod']
FUNCTION_NAMES = {'search': {'emma-search-get': 'get.py'},
                  'ingestion': {'emma-ingest-put': 'put.py',
                                'emma-ingest-get': 'recordGets.py',
                                'emma-ingest-delete': 'recordDeletes.py'
                                },
                  'maintenance': {'emma-maintenance-message': 'maintenance.py'}}

if target_param == 'all':
    targets = TARGET_LIST
else:
    targets = [target_param]

print("\nCommit ID: " + commit_id + " Env: " + env_param + " Target: " + target_param)

if commit_id == 'help':
    print("\nFormat: ")
    print("\n    ./deploy_commit_id COMMIT_ID [TARGET] [ENV]")
    print("\nThe commit ID is the full CodeCommit/git hash to be deployed.")
    print("Valid target arguments are ingestion, search, maintenance, or all. Default is all.")
    print("Valid env arguments for package and deploy are dev, qa, int, or staging.  Default is qa.")
    print(
        "\nMust be run in the [PROJECT_ROOT]/api/search/lambda/ directory, like ./deploy_commit_id.py test all\n")

else:
    for target in targets:
        for l_function in FUNCTION_NAMES[target].keys():
            l_function_env = l_function + "-" + env_param
            deploy_helpers.print_and_run(
                'aws lambda update-function-code ' + PROFILE_PARAM + ' --function-name '
                + l_function_env + ' --s3-bucket ' + S3_CODE_BUCKET_NAME + ' --s3-key '
                + commit_id + '/' + l_function + '.zip')
            deploy_helpers.write_lambda_commit_tags(l_function_env, commit_id, PROFILE_PARAM, S3_CODE_BUCKET_NAME)