#!/usr/bin/env python3
import json
import os
import shutil
import sys
from pathlib import Path
from dollar_ref import pluck, read_file
import deploy_helpers


# Set parameter defaults
target_param = "all"
task_param = "help"
env_param = "qa"
filename_param = "unset"

if len(sys.argv) > 4:
    s3_bucket_name = sys.argv[4]
if len(sys.argv) > 3:
    env_param = sys.argv[3]
if len(sys.argv) > 2:
    target_param = sys.argv[2]
if len(sys.argv) > 1:
    task_param = sys.argv[1]
    if task_param == "ingest":
        task_param = "ingestion"

print("\nTask: " + task_param + " Target: " + target_param + " Env: " + env_param)

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
SRC_DIRS = {'search': 'search', 'ingestion': 'ingestion', 'maintenance': 'maintenance'}


YAML_SCHEMA_FILE = '../schema/shared/model/common-domain-0.0.6.schema.yaml'
INGESTION_SCHEMA_FILE = "ingestion-record.schema.json"
ID_SCHEMA_FILE = "identifier-record.schema.json"
EMMA_PROFILE_ID_NUMBER = os.environ.get('PROFILE_ID', '')
LAMBDA_ARN_PREFIX = "arn:aws:lambda:us-east-1:" + EMMA_PROFILE_ID_NUMBER + ":function:"


def package(target, function_name, src_filename, req_file_name):
    """
    Copy the function script file to a directory and install all dependencies to that directory.
    Then, zip up the directory.
    """
    shutil.rmtree('deploy/' + function_name, True)
    try:
        os.makedirs('deploy/' + function_name)
    except FileExistsError:
        pass  # who cares?

    os.system('pipenv requirements > ' + req_file_name)
    os.system('pipenv run pip install -r ' + req_file_name +
              ' --no-deps -t deploy/' + function_name + "/")

    src_dir = SRC_DIRS[target]
    if 'ingestion' == target:
        copy_src_to_deploy(src_dir, [INGESTION_SCHEMA_FILE, ID_SCHEMA_FILE, src_filename, '__init__.py'], function_name)
        copy_dir_to_deploy('.', ['ingestion_handler', 'ingestion_validator', 'shared'], function_name)
    elif 'search' == target:
        copy_src_to_deploy(src_dir, [src_filename, '__init__.py'], function_name)
        shutil.copy(YAML_SCHEMA_FILE, 'deploy/' + function_name)
        copy_dir_to_deploy('.', ['shared', 'search_validator'], function_name)
    else:
        copy_src_to_deploy(src_dir, [src_filename, '__init__.py'], function_name)
        copy_dir_to_deploy('.', ['shared'], function_name)

    filePath = 'deploy/' + function_name + '.zip'
    try:
        os.remove(filePath)
    except:
        print("Error while deleting file : ", filePath)
    print_and_run('cd deploy/' + function_name +
                  ' && zip -r ../' + function_name + '.zip *')


def copy_src_to_deploy(src_dir, files, function_name):
    """
    Copy FILES to deploy folder
    """
    for src_filename in files:
        shutil.copy(src_dir + "/" + src_filename, 'deploy/' + function_name)


def copy_dir_to_deploy(src_dir, dirs, function_name):
    """
    Copy DIRECTORIES to deploy folder
    """
    for sub_dir in dirs:
        shutil.copytree(src_dir + "/" + sub_dir, 'deploy/' + function_name + '/' + sub_dir)


def update_schema(src_dir):
    """
    Whenever the schema changes in ../schema, this needs to be run to update the verification code in this project.
    """
    data = read_file(YAML_SCHEMA_FILE)
    export_json_schema(src_dir, data, INGESTION_SCHEMA_FILE, 'IngestionRecord')
    export_json_schema(src_dir, data, ID_SCHEMA_FILE, 'IdentifierRecord')
    puller_dir = str(Path.home()) + '/emma/emma-bookshare-puller/shared'
    if os.path.exists(puller_dir):
        shutil.copy(src_dir + "/" + INGESTION_SCHEMA_FILE, puller_dir)


def export_json_schema(src_dir, schema_data, filename, element_name):
    """
    Export just the parts of the schema we use for validation.
    """
    schema_resolved = pluck(schema_data, 'components', 'schemas', element_name)
    # Add jsonSchema properties not present in OpenAPI
    json_schema = {'$id': 'http://benetech.org/emma-federated-index/0.0.6/' + filename + '#',
                   '$schema': 'http://json-schema.org/draft-07/schema#',
                   '$comment': 'Generated from YAML OpenAPI definition by emma-federated-search/api/ingestion/lambda/emma-federated-ingest/make.py'}
    json_schema.update(schema_resolved)
    destination = src_dir + "/" + filename

    with open(destination, 'w') as out:
        raw_out = json.dumps(json_schema, indent=4)
        out.write(raw_out)


def print_and_run(command):
    """
    Print an OS command, then run it, returning the command return code.
    """
    print(command + "\n")
    return os.system(command)


"""
MAIN SECTION
"""
if task_param == 'schema':
    update_schema('ingestion')
elif task_param == 'help':
    print("\nFormat: ")
    print("\n    ./make.py TASK [TARGET] [ENV]")
    print("\nValid task arguments are help, schema, test, package, deploy, upload_s3, or deploy_s3. Default is help.")
    print("Valid target arguments are ingestion, search, maintenance, or all. Default is ingestion.")
    print("Valid env arguments for package and deploy are dev, qa, int, or staging.  Default is qa.")
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
    for target in targets:
        if target in TARGET_LIST:
            '''
            First, the targets which are the same regardless of which environment
            '''
            if task_param == 'test':
                if target != 'maintenance':
                    result_code = print_and_run('pipenv run python -m pytest '
                                  + 'tests/unit/' + SRC_DIRS[target] + '/test*.py -vv -s '
                                  + '--junitxml=test-reports/junit-' + target + '.xml '
                                  + '--log-file=test-reports/logs-' + target + '.txt')
                    test_result_codes = test_result_codes + result_code
            elif task_param == 'integration':
                if target != 'maintenance':
                    result_code = print_and_run('pipenv run python -m behave tests/integration/' + SRC_DIRS[target] + '/features/ -vv -s '
                                  + '--define env=' + env_param + ' '
                                  + '--junit '
                                  + '--junit-directory=integration-reports ')
                    test_result_codes = test_result_codes + result_code
            elif task_param == 'upload_s3':
                '''
                Uploads from specified environment-named file to general commit-named file
                '''
                commit_tag = deploy_helpers.get_commit_tag()
                deploy_helpers.write_commit_details(commit_tag, PROFILE_PARAM, S3_CODE_BUCKET_NAME)
                for l_function in FUNCTION_NAMES[target].keys():
                    l_function_env = l_function + "-" + env_param
                    l_function_env_zip = l_function_env + '.zip'
                    print_and_run(
                        'aws s3 cp '+ PROFILE_PARAM +' deploy/' + l_function_env_zip + ' s3://' + S3_CODE_BUCKET_NAME + '/' + commit_tag + '/' + l_function + '.zip')
                    deploy_helpers.write_s3_commit_tags(l_function + '.zip', commit_tag, PROFILE_PARAM, S3_CODE_BUCKET_NAME)
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
                                    'aws lambda update-function-code ' + PROFILE_PARAM + ' --function-name '
                                    + l_function_env + ' --zip-file fileb://deploy/' + l_function_env + '.zip')
                                commit_tag = deploy_helpers.get_commit_tag()
                                deploy_helpers.write_lambda_commit_tags(l_function_env, commit_tag, PROFILE_PARAM, S3_CODE_BUCKET_NAME)
                        elif task_param == 'deploy_s3':
                            for l_function in FUNCTION_NAMES[target].keys():
                                l_function_env = l_function + "-" + env
                                commit_tag = deploy_helpers.get_commit_tag()
                                print_and_run(
                                    'aws lambda update-function-code ' + PROFILE_PARAM + ' --function-name '
                                    + l_function_env  + ' --s3-bucket ' + S3_CODE_BUCKET_NAME + ' --s3-key '
                                    + commit_tag + '/' + l_function + '.zip')
                                deploy_helpers.write_lambda_commit_tags(l_function_env, commit_tag, PROFILE_PARAM, S3_CODE_BUCKET_NAME)

    print("done")
    if task_param in ['test', 'integration']:
        # A non-zero code means failure, zero code means success
        print("Exit code: " + str(test_result_codes))
        exit(test_result_codes)

