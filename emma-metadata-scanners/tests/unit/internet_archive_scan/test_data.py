import requests_mock
import re
import logging
from internet_archive_shared import config
from pprint import pprint

logger = logging.getLogger()
logger.setLevel(logging.INFO)

config.EMMA_INGESTION_URL = 'https://bogus.org/records'

def get_ia_search_response():
    with open('tests/unit/examples/ia_records_response.json') as data_file:
        data = data_file.read()
        return data

def get_ia_get_metadata():
    with open('tests/unit/examples/ia_metadata_response.json') as data_file:
        data = data_file.read()
        return data

def get_ia_scrape_response_first():
    with open('tests/unit/examples/ia_scrape_response_1.json') as data_file:
        data = data_file.read()
        return data

def get_ia_scrape_response_second():
    with open('tests/unit/examples/ia_scrape_response_2.json') as data_file:
        data = data_file.read()
        return data

def get_ia_scrape_response_last():
    with open('tests/unit/examples/ia_scrape_response_3_last.json') as data_file:
        data = data_file.read()
        return data

def match_page_1(request):
    return 'cursor' not in (request.url or '')

def match_page_2_cursor(request):
    return 'GET_PAGE_2_TOKEN' in (request.url or '')

def match_page_3_cursor(request):
    return 'GET_PAGE_3_TOKEN' in (request.url or '')

def match_first(request):
    return '100000000guineap0000kall' in str(request.body)

def match_second(request):
    return not '100000000guineap0000kall' in str(request.body)

ia_adv_search_matcher = re.compile('.*/advancedsearch.php.*')
ia_scrape_matcher = re.compile('.*/scrape.*')
ia_metadata_matcher = re.compile('.*/metadata.*')
emma_ingest_matcher = re.compile('.*/records.*')

def setup_mock(requests_mock):
    # Return some fake Internet Archive Scrape API calls for 3 pages of results
    requests_mock.post(ia_scrape_matcher, additional_matcher=match_page_1, text=get_ia_scrape_response_first())
    requests_mock.post(ia_scrape_matcher, additional_matcher=match_page_2_cursor, text=get_ia_scrape_response_second())
    requests_mock.post(ia_scrape_matcher, additional_matcher=match_page_3_cursor, text=get_ia_scrape_response_last())
    requests_mock.get(ia_adv_search_matcher, text=get_ia_search_response())
    requests_mock.get(ia_metadata_matcher, text=get_ia_get_metadata())

    # Return one successful EMMA ingestion result
    requests_mock.put(emma_ingest_matcher, text="", status_code=202)

def setup_mock_failure(requests_mock):
    # Return one successful and one unsucessful  EMMA ingestion result 
    requests_mock.put(emma_ingest_matcher, additional_matcher=match_first, text="", status_code=202)
    requests_mock.put(emma_ingest_matcher, additional_matcher= match_second, text="", status_code=429)

def setup_mock_partial_failure(requests_mock):
    # Return one successful and one partially sucessful EMMA ingestion result
    requests_mock.put(emma_ingest_matcher, additional_matcher=match_first, text="", status_code=202)
    requests_mock.put(emma_ingest_matcher, additional_matcher= match_second, text="", status_code=207)

def setup_mock_ingestion(requests_mock):
    # Return successful EMMA ingestion result
    requests_mock.put(emma_ingest_matcher, text="", status_code=202)