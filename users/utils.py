from oauthlib.oauth1 import Client


class CustomClient(Client):
    """
    Client used for the requests in the OAuth token process. 
    """
    def _render(self, request, formencode=False, realm=None):
        request.headers["User-Agent"] = "A useful user agent for ITS"
        return super()._render(request, formencode, realm)
