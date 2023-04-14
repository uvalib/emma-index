#!/usr/bin/env python3
'''
Build a single file schema for the search API

- Run from current directory
- If you don't want to run this through pipenv install the following modules to your system Python 3 installation:
    - dollar-ref
    - pyyaml
'''
import json
import shutil
import sys
from fileinput import FileInput
from pprint import pprint

import yaml

from dollar_ref import read_file, resolve

YAML_SEARCH_API_SCHEMA_FILE = 'emma-federated-search-api-0.0.6.yaml'
YAML_COMMON_SCHEMA_FILE = '../shared/model/common-domain-0.0.6.schema.yaml'
OUTPUT_SCHEMA_FILE = "emma-federated-search-api-0.0.6-singlefile.yaml"
OUTPUT_SWAGGERHUB_FILE = "emma-federated-search-api-0.0.6-swaggerhub.yaml"

DOMAIN_FILE_PATH = "../shared/model/common-domain-0.0.6.schema.yaml#"
SWAGGERHUB_DOMAIN_FILE_PATH= "https://api.swaggerhub.com/domains/bus/emma-federated-shared-components/0.0.6#"

def update_schema():
    data = read_file(YAML_SEARCH_API_SCHEMA_FILE)
    ig_api_schema_resolved = resolve(data, cwd='.', external_only=True)

    with open(OUTPUT_SCHEMA_FILE, 'w') as out:
        raw_out = yaml.dump(ig_api_schema_resolved, explicit_start=True,
            default_flow_style=False)
        out.write(raw_out)

def create_swaggerhub(input_file, output_file):
    shutil.copy(input_file, output_file)
    with FileInput(output_file, inplace=True) as file:
        for line in file:
            print(line.replace(DOMAIN_FILE_PATH, SWAGGERHUB_DOMAIN_FILE_PATH), end='')

update_schema()
create_swaggerhub(YAML_SEARCH_API_SCHEMA_FILE, OUTPUT_SWAGGERHUB_FILE)

print("done")
