#!/usr/bin/env python3
import fileinput
import glob
import os
import re
import shutil
import sys


# Set parameter defaults
target_param = "search"
task_param = "help"
env_param = "qa"


if len(sys.argv) > 3:
    env_param = sys.argv[3]
if len(sys.argv) > 2:
    target_param = sys.argv[2]
if len(sys.argv) > 1:
    task_param = sys.argv[1]

print("\nTask: " + task_param + " Target: " + target_param + " Env: " + env_param)

TARGET_LIST = ['search', 'count', 'espy']
FUNCTION_NAMES = {'search': {'emma-federated-search-es-test': 'get_passthrough.py'},
                  'count': {'emma-federated-search-es-count': 'get_passthrough.py'},
                  'espy': {'emma-federated-search-es-test': 'get_espy.py'} }
SRC_DIRS = {'search': 'search_function', 'count': 'search_function', 'espy': 'search_function' }

YAML_SCHEMA_FILE = '../schema/shared/model/common-domain-0.0.5.schema.yaml'

AWS_PROVIDED_MODULES = ['boto3', 'botocore', 'jmespath', 's3transfer', 'urllib3', 'six', 'docutils', 'python-dateutil', 'dateutil', 'python_dateutil-2.8.0.dist-info']

def package(target, function_name, src_filename, req_file_name):
    shutil.rmtree('deploy/' + function_name, True)
    try:
        os.makedirs('deploy/' + function_name)
    except FileExistsError:
        pass  # who cares?
    os.system('pipenv lock -r > ' + req_file_name)

    # Strip out AWS modules so we can use online IDE; may want to delete this in the future as it's not
    # Amazon's recommended approach.  Great for development and debugging, though.
    # Deploy size limit for online IDE is 3 MB
    for dep in AWS_PROVIDED_MODULES:
        with fileinput.FileInput(req_file_name, inplace=True) as file:
            for line in file:
                search_exp = r"" + dep + ".*$"
                print(re.sub(search_exp, '', line), end='')
    os.system('pipenv run pip install -r ' + req_file_name +
              ' --no-deps -t deploy/' + function_name + "/")
    for dep in AWS_PROVIDED_MODULES:
        shutil.rmtree('deploy/' + function_name + '/' + dep, True)
        for filePath in glob.glob('deploy/' + function_name + '/' + dep + '*'):
            try:
                os.remove(filePath)
            except:
                print("Error while deleting file : ", filePath)

    src_dir = SRC_DIRS[target]

    copy_src_to_deploy(src_dir, [src_filename, '__init__.py'], function_name)

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
    print(command + "\n")
    os.system(command)


if task_param == 'help':
    print("\nFormat: ")
    print("\n    ./make.py TASK [TARGET]")
    print("\nValid task arguments are help, schema, test, package, or deploy. Default is help.")
    print("Valid target arguments are search, count, espy, or all. Default is search.")
    print(
        "\nMust be run in the [PROJECT_ROOT]/api/search/lambda/ directory, like ./make.py test all\n")
else:
    if target_param == 'all':
        targets = TARGET_LIST
    else:
        targets = [target_param]

    if task_param == 'test':
        print_and_run('pipenv run python -m pytest tests/unit/test*.py -vv -s')
    for target in targets:
        if target in TARGET_LIST:
            if task_param == 'package':
                for l_function in FUNCTION_NAMES[target].keys():
                    req_file_name = l_function + "_reqs.txt"
                    filename = FUNCTION_NAMES[target][l_function]
                    print(filename)
                    package(target, l_function, filename, req_file_name)
            elif task_param == 'deploy':
                for l_function in FUNCTION_NAMES[target].keys():
                    print_and_run('aws lambda update-function-code --profile emma --function-name ' + l_function + ' --zip-file fileb://deploy/' + l_function + '.zip')

    print("done")
