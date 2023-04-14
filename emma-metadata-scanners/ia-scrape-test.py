#!/usr/bin/env python3
"""
Test to see if we can download more than 10,000 records from the internet archive scrape API
"""

import json
import requests
from shared import helpers

SEARCH_FIELDS = [
    'identifier',
    'indexdate',
    'subject',
    'title',
    'type',
]

SEARCH_FIELDS = [
    'addeddate',
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
    'oclc-id',
    'ocolc',
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

url = 'https://archive.org/services/search/v1/fields'
r = requests.get(url=url)
data = r.json()
print(json.dumps(data))
fields = data['fields']
fields.sort()
print(str(fields))

url = 'https://archive.org/services/search/v1/scrape'

page_size = 1000
# url = 'https://archive.org/services/search/v1/scrape'
q = '_exists_:indexdate AND collection:(trent_university OR oliverwendellholmeslibrary) AND mediatype:(texts) AND indexdate:[* TO 2019-12-01T22:45:40Z]z'
q = 'identifier:adreamofstonefam0000garv'

params = {'q': q, 'fields': ','.join(SEARCH_FIELDS), "count": page_size}


def try_scrape():
    for i in range(0, 11):
        r = requests.get(url=url, params=params)
        if r.status_code == 200:
            data = r.json()
            print(str(i) + ' ' + str(i * page_size) + ' ' + data['items'][0]['indexdate'])
            print(json.dumps(data['items'][0]))
            cursor = data['cursor']
            assert not helpers.exists(params, 'cursor') or params['cursor'] != cursor
            params['cursor'] = cursor
        else:
            print(r.content)


print(helpers.get_today_iso8601_datetime_pst())
print('Trying to retrieve > 10000 unsorted')
try_scrape()

print(helpers.get_today_iso8601_datetime_pst())

print('Trying to retrieve > 10000 sorted')
params['sorts'] = 'indexdate'
try_scrape()
print(helpers.get_today_iso8601_datetime_pst())
