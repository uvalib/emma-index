#!/usr/bin/env python3
import os
import shutil
import sys
import deploy_helpers

# Set parameter defaults
target_param = "bring_online"
task_param = "help"
env_param = "qa"

if len(sys.argv) > 3:
    env_param = sys.argv[3]
if len(sys.argv) > 2:
    target_param = sys.argv[2]
if len(sys.argv) > 1:
    task_param = sys.argv[1]

print("\nTask: " + task_param + " Target: " + target_param + " Env: " + env_param)

if os.getenv('CODEBUILD_RESOLVED_SOURCE_VERSION'):
    # We're in CodeBuild
    PROFILE_PARAM = ""
else:
    # We're logged in as a person
    PROFILE_PARAM = " --profile emma "

S3_CODE_BUCKET_NAME = 'emma-maintenance-scripts-deploy-packages'
TARGET_LIST = ['bring_online', 'take_offline']
ENV_LIST = ['dev', 'qa', 'staging', 'int', 'prod']
FUNCTION_NAMES = {'bring_online': {'emma-bring-online': 'bring_online.py'},
                  'take_offline': {'emma-take-offline': 'take_offline.py'
                                   }}
SRC_DIRS = {'bring_online': 'lambda_functions', 'take_offline': 'lambda_functions'}


def package(target, function_name, src_filename, req_file_name):
    shutil.rmtree('deploy/' + function_name, True)
    try:
        os.makedirs('deploy/' + function_name)
    except FileExistsError:
        pass  # who cares?

    if target in ['bring_online', 'take_offline']:
        os.system('pipenv lock -r > ' + req_file_name)
        os.system('pipenv run pip install -r ' + req_file_name +
                  ' --no-deps -t deploy/' + function_name + "/")

    src_dir = SRC_DIRS[target]

    copy_src_to_deploy(src_dir, [src_filename, '__init__.py'], function_name)
    copy_dir_to_deploy('.', ['shared', 'apigateway', 'scanners'], function_name)

    filePath = 'deploy/' + function_name + '.zip'
    try:
        os.remove(filePath)
    except:
        print("Error while deleting file : ", filePath)
    print_and_run('cd deploy/' + function_name +
                  ' && zip -r ../' + function_name + '.zip *')


def copy_src_to_deploy(src_dir, files, function_name):
    for src_filename in files:
        shutil.copy(src_dir + "/" + src_filename, 'deploy/' + function_name)


def copy_dir_to_deploy(src_dir, dirs, function_name):
    for sub_dir in dirs:
        shutil.copytree(src_dir + "/" + sub_dir, 'deploy/' + function_name + '/' + sub_dir)


def print_and_run(command):
    """
    Print an OS command, then run it, returning the command return code.
    """
    print(command + "\n")
    return os.system(command)


if task_param == 'help':
    print("\nFormat: ")
    print("\n    ./make.py TASK [TARGET] [ENV]")
    print("\nValid task arguments are help, test, package, or deploy. Default is help.")
    print("Valid target arguments are bring_online, take_offline, or all. Default is ingestion.")
    print("Valid env arguments for package and deploy are dev, qa, or staging.  Default is qa.")
    print(
        "\nMust be run in the [PROJECT_ROOT]/api/search/lambda/ directory, like ./make.py test all\n")
else:
    if target_param == 'all':
        targets = TARGET_LIST
    else:
        targets = [target_param]
    if env_param == 'all':
        envs = ENV_LIST
    else:
        envs = [env_param]

    test_result_codes = 0
    if task_param == 'test':
        result_code = print_and_run(
            'pipenv run python -m pytest '
            + 'tests/unit/test*.py -vv -s '
            + '--junitxml=test-reports/junit-maintenance-scripts.xml '
            + '--log-file=test-reports/logs-maintenance-scripts.txt')
        test_result_codes = test_result_codes + result_code
    elif task_param == 'integration':
        result_code = print_and_run(
            'pipenv run python -m behave tests/integration/features/ -vv -s '
            + '--define env=' + env_param + ' '
            + '--junit '
            + '--junit-directory=integration-reports ')
        test_result_codes = test_result_codes + result_code
    for target in targets:
        if target in TARGET_LIST:
            if task_param == 'upload_s3':
                '''
                Uploads from specified environment-named file to general commit-named file
                '''
                commit_tag = deploy_helpers.get_commit_tag()
                deploy_helpers.write_commit_details(commit_tag, PROFILE_PARAM, S3_CODE_BUCKET_NAME)
                for l_function in FUNCTION_NAMES[target].keys():
                    l_function_env = l_function + "-" + env_param
                    l_function_env_zip = l_function_env + '.zip'
                    print_and_run(
                        'aws s3 cp ' + PROFILE_PARAM + ' deploy/' + l_function_env_zip + ' s3://' + S3_CODE_BUCKET_NAME + '/' + commit_tag + '/' + l_function + '.zip')
                    deploy_helpers.write_s3_commit_tags(l_function + '.zip', commit_tag, PROFILE_PARAM,
                                                        S3_CODE_BUCKET_NAME)

            else:
                if 'deploy' in task_param:
                    commit_tag = deploy_helpers.get_commit_tag()
                    # Write a file with JSON information to a folder in S3
                    deploy_helpers.write_commit_details(commit_tag, PROFILE_PARAM, S3_CODE_BUCKET_NAME)
                for env in envs:
                    if env in ENV_LIST:
                        if task_param == 'package':
                            for l_function in FUNCTION_NAMES[target].keys():
                                req_file_name = 'deploy/' + l_function + "-" + env + "_reqs.txt"
                                filename = FUNCTION_NAMES[target][l_function]
                                print(filename)
                                package(target, l_function + "-" + env, filename, req_file_name)
                        elif task_param == 'deploy':
                            for l_function in FUNCTION_NAMES[target].keys():
                                l_function_env = l_function + "-" + env
                                print_and_run(
                                    'aws lambda update-function-code --profile emma --function-name ' + l_function_env + ' --zip-file fileb://deploy/' + l_function_env + '.zip')
                                if l_function == 'emma-ingest-put':
                                    print_and_run(
                                        'aws lambda update-function-code --profile emma --function-name ' + l_function + '-dev --zip-file fileb://deploy/' + l_function_env + '.zip')
                        elif task_param == 'deploy_s3':
                            for l_function in FUNCTION_NAMES[target].keys():
                                l_function_env = l_function + "-" + env
                                commit_tag = deploy_helpers.get_commit_tag()
                                print_and_run(
                                    'aws lambda update-function-code ' + PROFILE_PARAM + ' --function-name '
                                    + l_function_env + ' --s3-bucket ' + S3_CODE_BUCKET_NAME + ' --s3-key '
                                    + commit_tag + '/' + l_function + '.zip')
                                deploy_helpers.write_lambda_commit_tags(l_function_env, commit_tag, PROFILE_PARAM,
                                                                        S3_CODE_BUCKET_NAME)

    print("done")
    if task_param in ['test', 'integration']:
        # A non-zero code means failure, zero code means success
        print("Exit code: " + str(test_result_codes))
        exit(test_result_codes)