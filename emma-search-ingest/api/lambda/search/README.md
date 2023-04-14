# emma-federated-search

Lambda functions to support searching against the EMMA Federated Index on ElasticSearch

## Requirements

* AWS CLI with Administrator permission
* [Python 3.8 installed](https://www.python.org/downloads/)
* [Pipenv installed](https://github.com/pypa/pipenv)
    - `pip install pipenv`

Provided that you have requirements above installed, proceed by installing the application dependencies and development dependencies:

```bash
pipenv install
pipenv install -d
```

## Unit tests, Packaging, and Deployment 

Use the ```make.py``` script in the ```emma-federated-search/api/lambda``` folder
