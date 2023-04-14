#!/usr/bin/env python3

import os
import requests
import sys

def print_and_run(command):
    print(command + "\n")
    os.system(command)

# This secure piece of information should be set as an environment variable
API_KEY = os.environ.get('SWAGGERHUB_API_KEY', 'Unset')
OWNER = 'bus'
SEARCH_VERSION = '0.0.5'
INGESTION_VERSION = '0.0.5'
COMMON_VERSION = '0.0.5'

INGESTION_API = 'emma-federated-ingestion-api'
INGESTION_FILE = 'ingestion/emma-federated-index-ingestion-api-' + INGESTION_VERSION + '-swaggerhub.yaml'
SEARCH_API = 'emma-federated-search-api'
SEARCH_FILE = 'search/emma-federated-search-api-' + SEARCH_VERSION + '-swaggerhub.yaml'
COMMON_DOMAIN = 'emma-federated-shared-components'
COMMON_FILE = 'shared/model/common-domain-' + SEARCH_VERSION + '.schema.yaml'

api_names = { 'search' : SEARCH_API, 'ingestion' : INGESTION_API, 'common': COMMON_DOMAIN}
api_files = { 'search' : SEARCH_FILE, 'ingestion' : INGESTION_FILE, 'common': COMMON_FILE}
post_endpoints = { 
    'search' : '/apis/' + OWNER + '/' + SEARCH_API + '?oas=3.0.0&version=' + SEARCH_VERSION,
    'ingestion' : '/apis/' + OWNER + '/' + INGESTION_API + '?oas=3.0.0&version=' + INGESTION_VERSION,
    'common' : '/domains/' + OWNER + '/' + COMMON_DOMAIN + '?oas=3.0.0&version=' + SEARCH_VERSION
}

print_and_run('cd ingestion && ./make-schema.py')
print_and_run('cd search && ./make-schema.py')

headers={'Authorization' : API_KEY, "Content-Type" : "application/yaml"}

SWAGGERHUB_ROOT_URL='https://api.swaggerhub.com'

if len(sys.argv) > 1:
    task_param = sys.argv[1]
    targets = [ task_param ]
else:
    targets = api_names.keys()

for api in targets:
    with open(api_files[api]) as data_file1:
        payload = data_file1.read()
    url = SWAGGERHUB_ROOT_URL + post_endpoints[api]
    r = requests.post(url, data=payload, headers=headers)
    print ('Uploading ' + api_files[api] + ' to ' + r.url + '\n')
    
print("Make sure to update the schema for the lambda functions by running ./make.py schema in the api/lambda directory.")
print("")