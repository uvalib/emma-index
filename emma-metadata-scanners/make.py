#!/usr/bin/env python3
import fileinput
import glob
import os
import re
import shutil
import sys
import deploy_helpers

# Set parameter defaults
target_param = "bookshare_scan"
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

S3_CODE_BUCKET_NAME = 'emma-metadata-scanners-deploy-packages'
TARGET_LIST = ['bookshare_scan', 'ia_scan', 'ap_scan', 'hathi_scan', 'hathi_retry']
ENV_LIST = ['dev', 'qa', 'staging', 'int', 'prod']
FUNCTION_NAMES = {'bookshare_scan': 'bookshare-scan',
                  'ia_scan':'internet-archive-scan',
                  'ap_scan' : 'aceportal-scan',
                  'hathi_scan' : 'hathitrust-scan',
                  'hathi_retry' : 'hathitrust-retry'}
SRC_DIRS = {'bookshare_scan': 'bookshare_scan',
            'ia_scan': 'internet_archive_scan',
            'ap_scan': 'internet_archive_scan',
            'hathi_scan': 'hathitrust_scan',
            'hathi_retry': 'hathitrust_retry'}

FUNCTION_FILE_NAMES = {'bookshare_scan': 'bookshare_scan.py' ,
                       'ia_scan': 'internet_archive_scan.py',
                       'ap_scan' : 'internet_archive_scan.py',
                       'hathi_scan': 'hathitrust_scan.py',
                       'hathi_retry': 'hathitrust_retry.py'}

PROJECT_REMOVE_MODULES = {'bookshare_scan': ['internetarchive', 'internetarchive-1.9.0.dist-info'],
                          'ia_scan': ['requests-oauthlib'],
                          'ap_scan': ['requests-oauthlib'],
                          'hathi_scan': ['requests-oauthlib', 'oauthlib', 'oauthlib-3.1.0.dist-info', 'internetarchive',
                                         'internetarchive-1.9.0.dist-info'],
                          'hathi_retry': ['requests-oauthlib', 'oauthlib', 'oauthlib-3.1.0.dist-info',
                                          'internetarchive',
                                          'internetarchive-1.9.0.dist-info', 'pytz', 'jsonschema', 'jsonpath-ng',
                                          'pyisbn'], }


def remove_modules(module_list, req_file_name, function_name):
    for dep in module_list:
        with fileinput.FileInput(req_file_name, inplace=True) as file:
            for line in file:
                search_exp = r"" + dep + ".*$"
                print(re.sub(search_exp, '', line), end='')
    os.system('pipenv run pip install -r ' + req_file_name +
              ' --no-deps -t deploy/' + function_name + "/")
    for dep in module_list:
        shutil.rmtree('deploy/' + function_name + '/' + dep, True)
        for filePath in glob.glob('deploy/' + function_name + '/' + dep + '*'):
            try:
                os.remove(filePath)
            except:
                print("Error while deleting file : ", filePath)


def package(target, function_name, req_file_name):
    shutil.rmtree('deploy/' + function_name, True)
    try:
        os.makedirs('deploy/' + function_name)
    except FileExistsError:
        pass  # who cares?
    os.system('pipenv requirements > ' + req_file_name)

    # Maybe this should be refactored to only INCLUDE the relevant modules?  Or we just don't care and don't strip any out?
    remove_modules(PROJECT_REMOVE_MODULES[target], req_file_name, function_name)

    src_dir = SRC_DIRS[target]

    copy_src_to_deploy(src_dir, ['__init__.py'], function_name)
    copy_dir_to_deploy('.', ['shared'], function_name)

    if 'bookshare_scan' == target:
        copy_dir_to_deploy('.', ['bookshare_scan'], function_name)
        copy_dir_to_deploy('.', ['bookshare_shared'], function_name)
    if 'ia_scan' == target or 'ap_scan' == target:
        copy_dir_to_deploy('.', ['internet_archive_scan'], function_name)
        copy_dir_to_deploy('.', ['internet_archive_shared'], function_name)
    if 'hathi_scan' == target:
        copy_dir_to_deploy('.', ['hathitrust_scan'], function_name)
        copy_dir_to_deploy('.', ['hathitrust_shared'], function_name)
    if 'hathi_retry' == target:
        copy_dir_to_deploy('.', ['hathitrust_retry'], function_name)
        copy_dir_to_deploy('.', ['hathitrust_shared'], function_name)

    filePath = 'deploy/' + function_name + '.zip'
    try:
        os.remove(filePath)
    except:
        print("Error while deleting file : ", filePath)
    print_and_run('cd deploy/' + function_name +
              ' && zip -r ../' + function_name + '.zip *')


def copy_src_to_deploy(src_dir, files, function_name):
    for src_filename in files:
        shutil.copy(src_dir + "/" + src_filename, 'deploy/' + function_name )


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
    print("\nValid task arguments are help, test, package, deploy, upload_s3, or deploy_s3. Default is help.")
    print("Valid target arguments are bookshare_scan, ia_scan, hathi_scan, hathi_retry or all.  Default is bookshare_scan.")
    print("Valid env arguments for package and deploy are dev, qa, staging, int, or prod.  Default is qa.")
    print(
        "\nMust be run in the [PROJECT_ROOT] directory, like ./make.py test all\n")
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
            if task_param == 'test':
                result_code = print_and_run('pipenv run python -m pytest '
                                            + 'tests/unit/' + SRC_DIRS[target] + '/test*.py -vv -s '
                                            + '--junitxml=test-reports/junit-' + target + '.xml '
                                            + '--log-file=test-reports/logs-' + target + '.txt')
                test_result_codes = test_result_codes + result_code

            elif task_param == 'upload_s3':
                '''
                Uploads from specified environment-named file to general commit-named file
                '''
                commit_tag = deploy_helpers.get_commit_tag()
                deploy_helpers.write_commit_details(commit_tag, PROFILE_PARAM, S3_CODE_BUCKET_NAME)
                l_function = FUNCTION_NAMES[target]
                l_function_env = l_function + "-" + env_param
                l_function_env_zip = l_function_env + '.zip'
                print_and_run(
                    'aws s3 cp '+ PROFILE_PARAM +' deploy/' + l_function_env_zip + ' s3://' + S3_CODE_BUCKET_NAME + '/' + commit_tag + '/' + l_function + '.zip')
                deploy_helpers.write_s3_commit_tags(l_function + '.zip', commit_tag, PROFILE_PARAM, S3_CODE_BUCKET_NAME)
            for env in envs:
                if 'deploy' in task_param:
                    commit_tag = deploy_helpers.get_commit_tag()
                    # Write a file with JSON information to a folder in S3
                    deploy_helpers.write_commit_details(commit_tag, PROFILE_PARAM, S3_CODE_BUCKET_NAME)
                if env in ENV_LIST:
                    function_name = FUNCTION_NAMES[target] + '-' + env
                    req_file_name = "deploy/" + function_name + "_reqs.txt"

                    if task_param == 'package':
                        print("Packaging...")
                        package(target, function_name,  req_file_name)

                    elif task_param == 'deploy':
                        print_and_run('aws lambda update-function-code  ' + PROFILE_PARAM + '  --function-name ' + function_name + ' --zip-file fileb://deploy/' + function_name + '.zip')

                    elif task_param == 'deploy_s3':
                        l_function = FUNCTION_NAMES[target]
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