#!/usr/bin/env python3
'''
Build a single file schema for the ingest API

- Run from current directory
- If you don't want to run this through pipenv install the following modules to your system Python 3 installation:
    - dollar-ref
    - pyyaml
'''
import json
import re
import shutil
import sys
from fileinput import FileInput
from pprint import pprint

import yaml

from dollar_ref import read_file, resolve


YAML_INGEST_API_SCHEMA_FILE = 'emma-federated-index-ingestion-api-0.0.6.yaml'
YAML_COMMON_SCHEMA_FILE = '../shared/model/common-domain-0.0.6.schema.yaml'
OUTPUT_SCHEMA_FILE = "./emma-federated-index-ingestion-api-0.0.6-singlefile"
OUTPUT_SWAGGERHUB_FILE = "emma-federated-index-ingestion-api-0.0.6-swaggerhub.yaml"

DOMAIN_FILE_PATH = '../shared/model/common-domain-0.0.6.schema.yaml#'
SWAGGERHUB_DOMAIN_FILE_PATH= 'https://api.swaggerhub.com/domains/bus/emma-federated-shared-components/0.0.6#'

def update_schema(input_file, output_file):
    data = read_file(input_file)
    ig_api_schema_resolved = resolve(data, cwd='.', external_only=True)
    '''
    JSON instead
    with open(output_file + ".json", 'w') as out:
        raw_out = json.dumps(ig_api_schema_resolved, indent=4)
        out.write(raw_out)
    '''
    with open(output_file + ".yaml", 'w') as out:
        raw_out = yaml.dump(ig_api_schema_resolved, explicit_start=True,
        default_flow_style=False)
        out.write(raw_out)

def create_swaggerhub(input_file, output_file):
    shutil.copy(input_file, output_file)
    with FileInput(output_file, inplace=True) as file:
        for line in file:
            print(line.replace(DOMAIN_FILE_PATH, SWAGGERHUB_DOMAIN_FILE_PATH), end='')

update_schema(YAML_INGEST_API_SCHEMA_FILE, OUTPUT_SCHEMA_FILE)
create_swaggerhub(YAML_INGEST_API_SCHEMA_FILE, OUTPUT_SWAGGERHUB_FILE)
print("done")
