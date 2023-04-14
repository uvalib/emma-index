#!/usr/bin/env python3
"""
This is a test script that can be run independently of any lambda function to 
see if you can call the Internet Archive query endpoint.
"""

import os
from pprint import pprint
from internetarchive import get_session, search_items, get_item


IA_SECRET_KEY = os.environ.get('IA_SECRET_KEY', 'Missing')
IA_ACCESS_KEY = os.environ.get('IA_ACCESS_KEY', 'Missing')

IA_SESSION_CONFIG = {'s3': {'access': IA_ACCESS_KEY, 'secret': IA_SECRET_KEY}}
IA_SESSION = get_session(config=IA_SESSION_CONFIG)

search_params = {'rows': '5', 'page':'1', 'sort' : 'indexdate desc'}
search_fields = SEARCH_FIELDS = ['addeddate',
                 'avg_rating',
                 'backup_location',
                 'btih',
                 'call_number',
                 'collection',
                 'contributor',
                 'coverage',
                 'creator',
                 'createdate',
                 'date',
                 'description',
                 'downloads',
                 'external-identifier',
                 'foldoutcount',
                 'format',
                 'genre',
                 'headerImage',
                 'isbn',
                 'identifier',
                 'imagecount',
                 'indexflag',
                 'indexdate',
                 'item_size',
                 'language',
                 'lccn',
                 'licenseurl',
                 'mediatype',
                 'members',
                 'month',
                 'name',
                 'noindex',
                 'num_reviews',
                 'oai_updatedate',
                 'oclc',
                 'publicdate',
                 'publisher',
                 'related-external-id',
                 'reviewdate',
                 'rights',
                 'scanningcentre',
                 'source',
                 'stripped_tags',
                 'subject',
                 'title',
                 'type',
                 'updatedate',
                 'volume',
                 'week',
                 'year'
                 ]
# search_results = IA_SESSION.search_items(
#     "_exists_:indexdate AND collection:(trent_university) AND mediatype:(texts) AND indexdate:[* TO 2019-12-01T22:45:40Z]", params=search_params, fields=search_fields)

# for result in search_results:
#     pprint(result)

item=IA_SESSION.get_item('francisbaconstud0000pepp')
print(item.files)
