import json
import re

from shared import helpers, config
from ingestion_handler.UpsertHandler import UpsertHandler
from ingestion_validator.DocValidator import DocValidator
from tests.shared import test_helpers
import os

INGESTION_SCHEMA_FILE = 'ingestion-record.schema.json' if os.path.exists('ingestion-record.schema.json') \
    else 'ingestion/ingestion-record.schema.json'

docValidator = DocValidator(INGESTION_SCHEMA_FILE)


def test_title_id_hit(requests_mock):
    # Set up the data
    upsertHandler = UpsertHandler(config.EMMA_ELASTICSEARCH_INDEX, docValidator)
    es = config.ELASTICSEARCH_CONN
    elasticsearch_search_url_matcher = re.compile('.*_search.*')
    requests_mock.get(elasticsearch_search_url_matcher,
                      text=test_helpers.sample_title_hit_response())

    with open('tests/unit/ingestion/examples/harry-potter-1-brf-grade1.json') as data_file:
        data = data_file.read()
    doc = json.loads(data)
    del doc['emma_titleId']    
    # Run the test
    upsertHandler.update_emma_title_id(es, doc)
    # Check the results
    assert str(doc['emma_titleId']) == '100001'

def test_title_id_miss(requests_mock):
    # Set up the data
    upsertHandler = UpsertHandler(config.EMMA_ELASTICSEARCH_INDEX, docValidator)
    es = config.ELASTICSEARCH_CONN
    elasticsearch_search_url_matcher = re.compile('.*_search.*')
    requests_mock.get(elasticsearch_search_url_matcher,
                      text=test_helpers.sample_title_miss_response())
    with open('tests/unit/ingestion/examples/harry-potter-1-brf-grade1.json') as data_file:
        data = data_file.read()
    doc = json.loads(data)    
    del doc['emma_titleId']
    # Run the test
    upsertHandler.update_emma_title_id(es, doc)
    # Check the results
    assert len(str(doc['emma_titleId'])) > 20

def test_title_id_in_list(requests_mock):
    # Set up the data
    upsertHandler = UpsertHandler(config.EMMA_ELASTICSEARCH_INDEX, docValidator)
    es = config.ELASTICSEARCH_CONN
    elasticsearch_search_url_matcher = re.compile('.*_search.*')
    requests_mock.get(elasticsearch_search_url_matcher,
                      text=test_helpers.sample_title_miss_response())
    upsertHandler.current_title_ids = {}
    upsertHandler.current_title_ids['isbn:9780590353427'] = 'ABC123'
    with open('tests/unit/ingestion/examples/harry-potter-1-brf-grade1.json') as data_file:
        data = data_file.read()
    doc = json.loads(data)    
    del doc['emma_titleId']
    # Run the test
    upsertHandler.update_emma_title_id(es, doc)
    # Check the results
    assert str(doc['emma_titleId']) == 'ABC123'


def test_title_id_create_list(requests_mock):
    # Set up the data
    upsertHandler = UpsertHandler(config.EMMA_ELASTICSEARCH_INDEX, docValidator)
    es = config.ELASTICSEARCH_CONN
    elasticsearch_search_url_matcher = re.compile('.*_search.*')
    requests_mock.get(elasticsearch_search_url_matcher,
                      text=test_helpers.sample_title_miss_response())
    elasticsearch_bulk_url_matcher = re.compile('.*_bulk.*')
    requests_mock.post(elasticsearch_bulk_url_matcher,
                       text=test_helpers.sample_elasticsearch_put_response())
    with open('tests/unit/ingestion/examples/beatrix_potter_artifacts.json') as data_file:
        data = data_file.read()
    doc_list = json.loads(data)   
    errors = {} 
    # Run the test
    upsertHandler.submit(es, doc_list, errors)
    # Check the results
    # All results should have same title ID
    title_id = doc_list[0]['emma_titleId']
    for doc in doc_list:
        assert title_id == doc['emma_titleId']

def test_get_doc_id_prefix():
    with open('tests/unit/ingestion/examples/harry-potter-1-brf-grade1.json') as data_file:
        data = data_file.read()
    doc = json.loads(data)    
    prefix = helpers.get_doc_id_prefix(doc)
    assert prefix == 'bookshare-32480'

def test_truncate_publication_date():
    # Set up the data
    upsertHandler = UpsertHandler(config.EMMA_ELASTICSEARCH_INDEX, docValidator)
    document = {'emma_publicationDate' : '2021-11-02T20:26:59Z'}

    # Run the test
    upsertHandler.truncate_publication_date(document)

    # Check the results
    modified_date = document['emma_publicationDate']
    print(modified_date)
    assert modified_date == '2021-11-02'
