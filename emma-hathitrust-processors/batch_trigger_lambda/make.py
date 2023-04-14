#!/usr/bin/env python3
import os
import shutil
import sys
import deploy_helpers

# Set parameter defaults
task_param = "help"
env_param = "qa"
target_param = "trigger"

if len(sys.argv) > 2:
    env_param = sys.argv[2]
if len(sys.argv) > 1:
    task_param = sys.argv[1]

print("\nTask: " + task_param + " Env: " + env_param)

ENV_LIST = ['dev', 'qa', 'staging', 'int', 'prod']
FUNCTION_NAMES = {'trigger': 'hathitrust-batch-trigger'}

FUNCTION_FILE_NAMES = {'trigger': 'batch_trigger.py' }
S3_CODE_BUCKET_NAME = 'emma-hathitrust-processors-deploy-packages'

if os.getenv('CODEBUILD_RESOLVED_SOURCE_VERSION'):
    # We're in CodeBuild
    PROFILE_PARAM = ""
else:
    # We're logged in as a person
    PROFILE_PARAM = " --profile emma "

def package(target, function_name, req_file_name):
    shutil.rmtree('deploy/' + function_name, True)
    try:
        os.makedirs('deploy/' + function_name)
    except FileExistsError:
        pass  # who cares?
    os.system('pipenv lock -r > ' + req_file_name)

    shutil.copy(FUNCTION_FILE_NAMES[target], 'deploy/' + function_name)

    filePath = 'deploy/' + function_name + '.zip'
    try:
        os.remove(filePath)
    except:
        print("Error while deleting file : ", filePath)
    print_and_run('cd deploy/' + function_name +
              ' && zip -r ../' + function_name + '.zip *')


def print_and_run(command):
    """
    Print an OS command, then run it, returning the command return code.
    """
    print(command + "\n")
    return os.system(command)

if task_param == 'help':
    print("\nFormat: ")
    print("\n    ./make.py TASK [ENV]")
    print("\nValid task arguments are help, test, package, deploy, upload_s3, or deploy_s3. Default is help.")
    print("Valid env arguments for package and deploy are dev, qa, staging, int, or prod.  Default is qa.")
    print(
        "\nMust be run in the [PROJECT_ROOT] directory, like ./make.py test all\n")
else:
    test_result_codes = 0
    if env_param == 'all':
        envs = ENV_LIST
    else:
        envs = [env_param]
    for env in envs:
        print(env)
        if task_param == 'test':
            test_result_codes = print_and_run('pipenv run python -m pytest '
                                        + 'tests/unit/test*.py -vv -s '
                                        + '--junitxml=test-reports/junit-batch-trigger-lambda.xml '
                                        + '--log-file=test-reports/logs-batch-trigger-lambda.txt')
        if env in ENV_LIST:
            function_name = FUNCTION_NAMES[target_param]

            function_name_env = FUNCTION_NAMES[target_param] + '-' + env
            function_name_zip = function_name + '.zip'

            req_file_name = "deploy/" + function_name_env + "_reqs.txt"



            if task_param == 'package':
                print("Packaging...")
                package(target_param, function_name_env, req_file_name)

            elif task_param == 'deploy':
                print_and_run('aws lambda update-function-code  ' + PROFILE_PARAM + '  --function-name ' + function_name_env + ' --zip-file fileb://deploy/' + function_name_env + '.zip')
            elif task_param == 'deploy_s3':
                commit_tag = deploy_helpers.get_commit_tag()
                print_and_run(
                    'aws lambda update-function-code ' + PROFILE_PARAM + ' --function-name '
                    + function_name_env + ' --s3-bucket ' + S3_CODE_BUCKET_NAME + ' --s3-key '
                    + commit_tag + '/' + function_name + '.zip')
                deploy_helpers.write_lambda_commit_tags(function_name_env, commit_tag, PROFILE_PARAM,
                                                        S3_CODE_BUCKET_NAME)
            elif task_param == 'upload_s3':
                '''
                Uploads from specified environment-named file to general commit-named file
                '''
                commit_tag = deploy_helpers.get_commit_tag()
                deploy_helpers.write_commit_details(commit_tag, PROFILE_PARAM,
                                                    S3_CODE_BUCKET_NAME)

                print_and_run(
                    'aws s3 cp ' + PROFILE_PARAM + ' deploy/' + function_name_zip + ' s3://' + S3_CODE_BUCKET_NAME
                    + '/' + commit_tag + '/' + function_name + '.zip')
                deploy_helpers.write_s3_commit_tags(function_name + '.zip', commit_tag, PROFILE_PARAM,
                                                    S3_CODE_BUCKET_NAME)
    print("done")
    if task_param in ['test', 'integration']:
        # A non-zero code means failure, zero code means success
        print("Exit code: " + str(test_result_codes))
        exit(test_result_codes)
