#!/usr/bin/env python3
"""
This is a test script that can be run independently of any lambda function to 
see if you make an OAuth2 authenticated call to the Bookshare V2 API /catalog
endpoint.  Defaults to QA.
"""

import os
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session


BKS_CLIENT_ID = os.environ.get('BKS_API_KEY', 'Missing')
BKS_USERNAME = os.environ.get('BKS_API_USERNAME', 'Missing')
BKS_PASSWORD = os.environ.get('BKS_API_PASSWORD', 'Missing')
BKS_BASE_URL = os.environ.get('BKS_API_BASE_URL', 'https://api.qa.bookshare.org/v2')
BKS_TOKEN_URL = os.environ.get('BKS_API_TOKEN_URL', 'https://auth.qa.bookshare.org/oauth/token')

BKS_API_KEY_PARAM = {'api_key': BKS_CLIENT_ID}
oauth = OAuth2Session(client=LegacyApplicationClient(client_id=BKS_CLIENT_ID))
oauth.params = BKS_API_KEY_PARAM
token = oauth.fetch_token(token_url=BKS_TOKEN_URL,
        username=BKS_USERNAME, password=BKS_PASSWORD, client_id=BKS_CLIENT_ID, client_secret='')

print(token)

r = oauth.get(BKS_BASE_URL + '/catalog')
print (r.content)