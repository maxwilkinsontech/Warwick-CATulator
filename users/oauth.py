"""
Methods that are used to authenticate the user with the Warwick
oauth API
"""
import urllib.parse

from oauthlib.oauth1 import SIGNATURE_HMAC, SIGNATURE_TYPE_AUTH_HEADER
from requests_oauthlib import OAuth1Session

from .utils import CONSUMER_KEY, CONSUMER_SECRET, CustomClient
from .models import User, RequestTokenStore
from .tabula import retreive_member_infomation


ACCESS_TOKEN_URL = "https://websignon.warwick.ac.uk/oauth/accessToken"
AUTHORISE_URL = "https://websignon.warwick.ac.uk/oauth/authorise?"
REQUEST_TOKEN_URL = "https://websignon.warwick.ac.uk/oauth/requestToken?"

SCOPES = "urn:websignon.warwick.ac.uk:sso:service urn:tabula.warwick.ac.uk:tabula:service"

def obtain_request_token(callback='http://127.0.0.1:8000/callback/', expiry='forever'):
    """
    This method obtains a request token by sending a signed request and returns 
    a url to redirect the user to authorize the token.
    """
    oauth = OAuth1Session(
        CONSUMER_KEY, 
        client_secret=CONSUMER_SECRET,
        signature_method=SIGNATURE_HMAC,
        signature_type=SIGNATURE_TYPE_AUTH_HEADER, 
        client_class=CustomClient,
        callback_uri=callback
    )
    response = oauth.fetch_request_token(
        url=REQUEST_TOKEN_URL + urllib.parse.urlencode({'scope': SCOPES, 'expiry': expiry}))
    # store the oauth_token_secret for later use when getting access token
    RequestTokenStore.objects.create(
        oauth_token=response['oauth_token'],
        oauth_token_secret=response['oauth_token_secret']
    )

    authorise_qs = urllib.parse.urlencode({'oauth_token': response['oauth_token']})
    return AUTHORISE_URL + authorise_qs


def exchange_access_token(oauth_token, returned_url, user_id):
    """
    This method gets an access token using an authorized request token.
    """
    aouth_secret = RequestTokenStore.get_secret(oauth_token)
    oauth = OAuth1Session(
        CONSUMER_KEY,
        CONSUMER_SECRET,
        resource_owner_secret=aouth_secret, 
        client_class=CustomClient
    )
    # TODO: process error
    oauth.parse_authorization_response(returned_url)
    access_tokens = oauth.fetch_access_token(ACCESS_TOKEN_URL)
    # get or create user
    user = User.objects.filter(user_id=user_id).first()
    if user is None:
        user = User.objects.create(
            email=user_id+'@email.com',
            user_id=user_id,
            access_token=access_tokens['oauth_token'],
            access_token_secret=access_tokens['oauth_token_secret']
        )
        retreive_member_infomation(user)
    else:
        user.access_token = access_tokens['oauth_token']
        user.access_token_secret = access_tokens['oauth_token_secret']
        user.save()

    return user