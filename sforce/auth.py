from __future__ import unicode_literals
import requests
from requests_oauthlib import OAuth1
from urlparse import parse_qs, urlunparse
from urllib import quote_plus
from pprint import pprint

class Connect(object):
    def __init__(self, client_key=None, client_secret=None,
                 callback_uri=None, sandbox=False):
        self.client_key = client_key
        self.client_secret = client_secret
        self.callback_uri = callback_uri
        self.request_path = "/_nc_external/system/security/oauth/RequestTokenHandler"
        self.authorize_path = "/setup/secur/RemoteAccessAuthorizationPage.apexp"
        self.access_path = "/_nc_external/system/security/oauth/AccessTokenHandler"
        self.oauth = OAuth1(self.client_key, client_secret=self.client_secret,
                            callback_uri=self.callback_uri)
        self.oauth_token = None
        self.oauth_token_secret = None
        self.sandbox = sandbox

    @property
    def _root_url(self):
        if self.sandbox:
            return "https://test.salesforce.com"
        return "https://login.salesforce.com"

    def request(self):
        """ Request phase """
        request_url = self._root_url + self.request_path
        r = requests.post(url=request_url, auth=self.oauth)
        credentials = parse_qs(r.content)
        self.oauth_token = credentials.get('oauth_token')[0]
        self.oauth_token_secret = credentials.get('oauth_token_secret')[0]

    def authorize(self):
        """ Authorize phase """
        authorize_url_root = self._root_url + self.authorize_path
        authorize_url_query = "?oauth_token=%s&oauth_consumer_key=%s" % (self.oauth_token, self.client_key)
        authorize_url = authorize_url_root + authorize_url_query
        return authorize_url

    def access(self, verifier):
        """ Access phase """
        access_url = self._root_url + self.access_path
        oauth = OAuth1(self.client_key,
                       client_secret=self.client_secret,
                       resource_owner_key=self.oauth_token,
                       resource_owner_secret=self.oauth_token_secret,
                       verifier=verifier)
        r = requests.post(url=access_url, auth=oauth)
        credentials = parse_qs(r.content)
        self.oauth_token = credentials.get('oauth_token')[0]
        self.oauth_token_secret = credentials.get('oauth_token_secret')[0]

