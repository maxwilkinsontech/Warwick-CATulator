"""
Methods that are used to authenticate the user with the Warwick
oauth API
"""
import json
import requests

from requests_oauthlib import OAuth1
from urllib.parse import parse_qs
from django.http import HttpResponse

client_key = 'warwickcatulator.co.uk'
client_secret = 'TGVhdmUgdGhlIGtleSB0eXBlIyZXQu'

def obtain_request_token():
    """
    This method obtains a request token by sending a signed request.
    """
    request_token_url = 'https://websignon.warwick.ac.uk/oauth/requestToken'
    body = {'scope': 'urn:websignon.warwick.ac.uk:sso:service'}
    # obtain request token
    oauth = OAuth1(client_key, client_secret=client_secret)
    response = requests.post(url=request_token_url, auth=oauth, data=body)
    credentials = parse_qs(response.content.decode('utf-8'))
    resource_owner_key = credentials.get('oauth_token')[0]
    resource_owner_secret = credentials.get('oauth_token_secret')[0]
    # authorize the request token
    request_token_auth_url = ('https://websignon.warwick.ac.uk/oauth/authorise'
                              '?oauth_token=' + resource_owner_key + 
                              '&oauth_callback=http://127.0.0.1:8000/get-access-token/'
                             )

    return request_token_auth_url

def exchange_access_token(oauth_token, user_id):
    """
    This method gets an access token using an authorized request token.
    """
    request_token_url = 'https://websignon.warwick.ac.uk/oauth/accessToken'
    oauth = OAuth1(client_key, client_secret=client_secret, resource_owner_key=oauth_token)
    response = requests.post(url=request_token_url, auth=oauth)


    print(response.status_code)
    print(response.reason)
    print(response.content)