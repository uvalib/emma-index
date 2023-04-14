import logging

from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session

from bookshare_shared import config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

oauth = OAuth2Session(client=LegacyApplicationClient(client_id=config.BKS_CLIENT_ID))
oauth.params = config.BKS_API_KEY_PARAM
oauth.headers = config.BKS_HEADERS


def fetch_token() :
    try:
        token = oauth.fetch_token(token_url=config.BKS_TOKEN_URL,
                username=config.BKS_USERNAME, password=config.BKS_PASSWORD, client_id=config.BKS_CLIENT_ID, client_secret='')
        return token
    except Exception as e:
        logger.error("Can't get OAuth2 Token for " + config.BKS_USERNAME)
        logger.error (str(e))
 
fetch_token()
