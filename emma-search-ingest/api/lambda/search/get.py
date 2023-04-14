'''
get.py
AWS Lambda function emma-federated-search-get
Search the EMMA Federated Index for records
'''
import json
import pprint
import regex
import shared.config
from elasticsearch_dsl import Search, Q
from search_validator.Validator import Validator
from shared.alias_utils import copy_to_new_field_names
from shared.helpers import exists, get_multi_param, safe_del, listify_record

# Global variables are reused across execution contexts (if available)

INDEX = shared.config.EMMA_ELASTICSEARCH_INDEX
URL = 'https://' + shared.config.EMMA_ELASTICSEARCH_HOST + '/' + INDEX + '/_search'

es = shared.config.ELASTICSEARCH_CONN


def lambda_handler(event, context):
    """
    Top-level function that handles the call to the lambda function coming from AWS.
    Converts the incoming event to a call to ElasticSearch and returns the results.
    """
    query_string_parameters = event.get('queryStringParameters', {})
    multi_string_parameters = event.get('multiValueQueryStringParameters', {})
    validation_errors = []
    validator = Validator(query_string_parameters, multi_string_parameters)
    validator.validate(validation_errors)

    if not validation_errors:
        pprint.pprint(query_string_parameters)
        results, code = get_es_results(query_string_parameters, multi_string_parameters)
    else:
        results, code = validation_errors, 400

    if query_string_parameters and exists(query_string_parameters, 'pretty'):
        body = json.dumps(results, sort_keys=True, indent=4)
    else:
        body = json.dumps(results)

    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": body
    }


def build_query(query_string_params, multi_string_params, extra_es_params, errors):
    """
    Build the query
    """
    es_search = Search(using=es, index=INDEX, extra=extra_es_params)

    if exists(query_string_params, 'q'):
        quick_query = query_string_params['q']

        # Separate strings that contain any numbers to search against numeric (potential ID) fields
        numeric_strings = list(filter(lambda x: any(char.isdigit() for char in x), quick_query.split()))

        should_haves = []
        if numeric_strings is not None and len(numeric_strings) > 0:
            should_haves.append(Q({"multi_match": {"query": ' '.join(numeric_strings), "fields": [
                "dc_identifier.numeric", "dc_relation.numeric"]}}))
        should_haves.append(Q({"multi_match": {"query": quick_query, "fields": [
            "dc_title.en^4", "dc_creator^4", "dc_identifier", "dc_relation"]}}))
        if exists(query_string_params, 'publisher'):
            must_haves = [
                Q({"match": {"dc_publisher": {"query": query_string_params['publisher'], "operator": "and"}}})]
            es_search = es_search.query(Q('bool', should=should_haves, must=must_haves))
        else:
            es_search = es_search.query(Q('bool', should=should_haves))
    else:
        must_haves = []
        if exists(query_string_params, 'title'):
            must_haves.append(Q({"match": {"dc_title": {"query": query_string_params['title'], "operator": "and"}}}))
        if exists(query_string_params, 'creator'):
            must_haves.append(
                Q({"match": {"dc_creator": {"query": query_string_params['creator'], "operator": "and"}}}))
        if exists(query_string_params, 'identifier'):
            must_haves.append(Q(
                {"match": {"dc_identifier.numeric": {"query": query_string_params['identifier'], "operator": "and"}}}))
        if exists(query_string_params, 'publisher'):
            must_haves.append(
                Q({"match": {"dc_publisher": {"query": query_string_params['publisher'], "operator": "and"}}}))
        es_search = es_search.query(Q('bool', must=must_haves))

    es_search = add_multi_param('format', 'dc_format', query_string_params, multi_string_params, es_search)
    es_search = add_multi_param('formatFeature', 'emma_formatFeature', query_string_params, multi_string_params,
                                es_search)
    es_search = add_multi_param('accessibilityFeature', 's_accessibilityFeature', query_string_params,
                                multi_string_params, es_search)
    es_search = add_multi_param('collection', 'emma_collection', query_string_params, multi_string_params, es_search)

    if exists(query_string_params, 'formatVersion'):
        es_search = es_search.filter(
            "term", emma_formatVersion=query_string_params['formatVersion'])

    if exists(query_string_params, 'repository'):
        repository_param = query_string_params['repository']
        es_search = es_search.filter("term", emma_repository=repository_param)

    es_search = add_date_filter(es_search, query_string_params, errors, 'sortDate', 'emma_sortDate')
    es_search = add_date_filter(es_search, query_string_params, errors, 'lastRemediationDate',
                                'emma_lastRemediationDate')
    es_search = add_date_filter(es_search, query_string_params, errors, 'publicationDate',
                                'emma_publicationDate')
    return es_search, errors



def add_estimated_max_relevance_score(query_string_params, multi_string_params, extra_es_params):
    """
    Do a pre-flight search for a sense of the relevance score, then add it to the query
    """
    relevance_extra_params = get_extra(query_string_params, [])
    relevance_extra_params['track_scores'] = True
    relevance_extra_params['size'] = 1
    (relevance_estimate_search, rel_est_errors) = \
        build_query(query_string_params, multi_string_params, relevance_extra_params, [])
    relevance_estimate_search = add_sort(relevance_estimate_search, query_string_params, rel_est_errors)

    if exists(query_string_params, 'logquery'):
        print("Relevance Query in JSON")
        pp = pprint.PrettyPrinter(indent=4)
        print(pp.pformat(relevance_estimate_search.to_dict()))

    relevance_estimate_response = relevance_estimate_search.execute()
    relevance_estimate_max_score = relevance_estimate_response['hits']['max_score']
    if exists(query_string_params, 'logquery'):
        print("Relevance Response")
        print(json.dumps(relevance_estimate_response.to_dict(), indent=4))

    if relevance_estimate_max_score:
        '''
        Add a cutoff at 70% of the maximum relevance
        '''
        relevance_threshold = float(relevance_estimate_max_score) * 0.7
        print("max_score  " + str(relevance_estimate_max_score) + " relevance_threshold " + str(relevance_threshold))
        # Update main query
        extra_es_params['min_score'] = relevance_threshold
        extra_es_params['track_scores'] = True


def build_query_with_relevance(query_string_params, multi_string_params):
    """
    If sorting by title or date is enabled, it makes ElasticSearch's amazing relevance capabilities pretty useless.
    In this case, only return results above a certain relevance threshold.
    Because the threshold can vary wildly, get the max score result as a starting point.
    """
    errors = []
    extra_es_params = get_extra(query_string_params, errors)

    if exists(query_string_params, 'sort'):
        add_estimated_max_relevance_score(query_string_params, multi_string_params, extra_es_params)
        (es_search, errors) = build_query(query_string_params, multi_string_params, extra_es_params, errors)
        es_search = add_sort(es_search, query_string_params, errors)
    else:
        # No sorting (other than default relevance sort.)
        (es_search, errors) = build_query(query_string_params, multi_string_params, extra_es_params, errors)

    return es_search, errors


def add_date_filter(query, query_string_params, errors, input_param, output_param):
    if exists(query_string_params, input_param):
        date_param = query_string_params[input_param]
        query = query.filter(
            "range", **{output_param : {"gte": query_string_params[input_param]}})
    return query


def add_sort(query, query_string_params, errors):
    if exists(query_string_params, 'sort'):
        sort_param = query_string_params['sort']
        if sort_param == 'title':
            query = query.sort({'emma_sortTitle': {"order": "asc", "missing": "_last"}}, 'emma_recordId')
        elif sort_param == 'publicationDate':
            query = query.sort({'emma_publicationDate': {"order": "desc", "missing": "_last"}}, 'emma_recordId')
        elif sort_param == 'lastRemediationDate':
            query = query.sort({'emma_lastRemediationDate': {"order": "desc", "missing": "_last"}}, 'emma_recordId')
        elif sort_param == 'sortDate':
            query = query.sort({'emma_sortDate': {"order": "desc"}},
                               'emma_recordId')
    return query


def get_extra(query_string_params, errors):
    """
    Set parameters the Elasticsearch DSL API considers "extra",
    related to paging and sorting.

    Two ways to page depending on how we sort
    1. Sorting title or date: use searchAfterValue and searchAfterId
    2. Default sorting using relevance: use "from"
    Method #1 is preferred for better durability against high demand and DDOS attacks
    Method #2 is included for a small number of results (1000 total) because an explicit sort is needed to use "search after"
    """

    extra = {}

    max_page_size = 100
    if exists(query_string_params, 'group'):
        group_param_value = query_string_params['group']
        group = {
            'field': group_param_value,
            'inner_hits': {
                'name': 'related',
                'size': 15
            }
        }
        max_page_size = 10
        extra['collapse'] = group

    size = get_page_size(query_string_params, max_page_size)
    extra['size'] = size

    if exists(query_string_params, 'searchAfterValue') and exists(query_string_params, 'searchAfterId'):
        search_after_value = query_string_params['searchAfterValue']
        '''
        The substitution strips out non (Unicode defined) alphanumeric characters
        so that the searchAfterValue will match the emma_sortTitle field.
        '''
        if exists(query_string_params, 'sort') and query_string_params['sort'] == 'title':
            search_after_value = regex.sub("[^\\p{Alnum} ]", "", search_after_value)
        search_after = [search_after_value, query_string_params['searchAfterId']]
        extra['search_after'] = search_after
    if exists(query_string_params, 'from'):
        from_param = query_string_params['from']
        if not exists(query_string_params, 'sort'):
            extra['from'] = from_param
    return extra


def get_page_size(query_string_params, max_size):
    page_size = max_size
    if exists(query_string_params, 'size'):
        size_int = int(query_string_params['size'])
        if size_int < max_size:
            page_size = size_int
    return page_size


def add_multi_param(param_name, term_name, query_string_params, multi_string_params, es_search):
    """
    For parameters that can have multiple values, get them from the correct API gateway list, validate, and
    add to search filters
    """
    if exists(query_string_params, param_name):
        value_list = get_multi_param(param_name, query_string_params, multi_string_params)
        if value_list is not None:
            es_search = es_search.filter("terms", **{term_name: value_list})
    return es_search


def is_group_result(hit):
    return exists(hit, 'inner_hits')


def cleanup_record(record):
    # Fields we're not making public.  Who knows, they might change.
    safe_del(record, 'emma_indexLastUpdated')
    safe_del(record, 'emma_sortTitle')
    safe_del(record, 'dc_provenance')
    safe_del(record, 'rem_remediationComments')
    safe_del(record, 'periodical_title')
    safe_del(record, 'periodical_identifier')
    safe_del(record, 'periodical_series_position')

    # The following two misspelled fields were added to the ElasticSearch search mapping
    safe_del(record, 'emma_dateSort')
    safe_del(record, 'emma_titleSort')


def logquery(es_search):
    print("Query in JSON")
    pp = pprint.PrettyPrinter(indent=4)
    print(pp.pformat(es_search.to_dict()))


def get_es_results(query_string_parameters, multi_string_parameters):
    """
    Send a query to ElasticSearch and clean up the results to match the OpenAPI definition.
    """
    (es_search, errors) = build_query_with_relevance(query_string_parameters, multi_string_parameters)

    if exists(query_string_parameters, 'logquery'):
        logquery(es_search)

    results = errors

    if len(errors) == 0:
        es_response = es_search.execute()

        # Add the search results to the response
        transformed_results = []
        response_dict = es_response.to_dict()

        for hit in response_dict['hits']['hits']:
            record = listify_record(hit['_source'])
            cleanup_record(record)
            copy_to_new_field_names(record)
            if is_group_result(hit):
                inner_results = []
                for inner_hit in hit['inner_hits']['related']['hits']['hits']:
                    # sometimes ? elasticsearch_dsl does not recursively convert back to Python native types
                    # inner_hit = inner_hit.to_dict()
                    inner_record = inner_hit['_source']
                    inner_record = listify_record(inner_record)
                    copy_to_new_field_names(inner_record)
                    cleanup_record(inner_record)
                    inner_results.append(inner_record)
                record['related_records'] = inner_results
            transformed_results.append(record)

        results = transformed_results
        code = 200
    else:
        # Bad input!
        code = 400

    return (results, code)
