#!/usr/bin/env python3
import fileinput
import glob
import json
import os
import re
import shutil
import sys
from pathlib import Path


from dollar_ref import pluck, read_file

# Set parameter defaults
target_param = "metrics"
task_param = "help"
env_param = "qa"


if len(sys.argv) > 3:
    env_param = sys.argv[3]
if len(sys.argv) > 2:
    target_param = sys.argv[2]
if len(sys.argv) > 1:
    task_param = sys.argv[1]

print("\nTask: " + task_param + " Target: " + target_param + " Env: " + env_param)

TARGET_LIST = ['metrics', 'publish']
ENV_LIST = ['dev', 'qa', 'staging', 'int', 'prod']
FUNCTION_NAMES = {'metrics': {'emma-cloudwatch-metrics' : 'get.py'}, 'publish': {'emma-publish-counts' : 'publish_counts.py'}}
SRC_DIRS = {'metrics': 'metrics', 'publish': 'publish' }


AWS_PROVIDED_MODULES = ['boto3', 'botocore', 'jmespath', 's3transfer', 'urllib3', 'six', 'docutils', 'python-dateutil', 'dateutil', 'python_dateutil-2.8.0.dist-info']

def copy_dir_to_deploy(src_dir, dirs, function_name):
    for sub_dir in dirs:
        shutil.copytree(src_dir + "/" + sub_dir, 'deploy/' + function_name + '/' + sub_dir)

def package(target, function_name, src_filename, req_file_name):
    shutil.rmtree('deploy/' + function_name, True)
    try:
        os.makedirs('deploy/' + function_name)
    except FileExistsError:
        pass  # who cares?
    os.system('pipenv lock -r > ' + req_file_name)

    os.system('pipenv run pip install -r ' + req_file_name +
              ' --no-deps -t deploy/' + function_name + "/")

    src_dir = SRC_DIRS[target]
    copy_dir_to_deploy('.', [src_dir], function_name)
    file_path = 'deploy/' + function_name + '.zip'
    try:
        os.remove(file_path)
    except:
        print("Error while deleting file : ", file_path)

    print_and_run('cd deploy/' + function_name + ' && zip -r ../' + function_name + '.zip *')


def print_and_run(command):
    print(command + "\n")
    os.system(command)

if task_param == 'help':
    print("\nFormat: ")
    print("\n    ./make.py TASK [TARGET] [ENV]")
    print("\nValid task arguments are help, test, package, or deploy. Default is help.")
    print("Valid target arguments are metrics. Default is metrics.")
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

    for target in targets:
        if target in TARGET_LIST:
            if task_param == 'test':
                print_and_run('pipenv run python -m pytest tests/unit/' + SRC_DIRS[target] + '/test*.py -vv -s')
            else:
                for env in envs:
                    if env in ENV_LIST:
                        if task_param == 'package':
                            for l_function in FUNCTION_NAMES[target].keys():
                                req_file_name = 'deploy/' + l_function + "-" + env + "_reqs.txt"
                                filename = FUNCTION_NAMES[target][l_function]
                                print(filename)
                                package(target, l_function+ "-" + env, filename, req_file_name)
                        elif task_param == 'deploy':
                            for l_function in FUNCTION_NAMES[target].keys():
                                l_function_env = l_function + "-" + env
                                print_and_run('aws lambda update-function-code --profile emma --function-name ' + l_function_env + ' --zip-file fileb://deploy/' + l_function_env + '.zip')
                                if l_function == 'emma-ingest-put':
                                    print_and_run('aws lambda update-function-code --profile emma --function-name ' + l_function + '-dev --zip-file fileb://deploy/' + l_function_env + '.zip')

    print("done")
