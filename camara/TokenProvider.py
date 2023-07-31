import datetime

import requests


class TokenProvider:
    """
    Abstraction for anything and everything token related.

    You need the time left on the token? Use this provider. Also good for refreshing a token if out dated, or creating
    a completely new one.
    """

    def __init__(self, client_id, client_secret, auth_url):
        """
        Initialize a token provider

        Please provide with all needed information to create a token following open id specification.

        :param: client_id the associated client id
        :param: client_secret the secret for the authentication
        :param: auth_url the url to be called to create a token based on the other given parameters
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = auth_url
        self.token = None
        self.auth_responses = []

    def create_access_token(self):
        """
        Uses the client secret and client id to request an authentication token.

        Upon successful request, the token is stored internally. Once created,
         it's :func:`time left <camara.Camara.token_seconds_remaining>` and
         :func:`expiration state <camara.Camara.is_token_expired>` can be retrieved.

        :return: the request, response tuple of the operation.
        """
        payload = f'grant_type=client_credentials&client_id={self.client_id}&client_secret={self.client_secret}'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.request("POST", self.auth_url, headers=headers, data=payload)

        if response.status_code == 200:
            token_response = response.json()
            token_response['created_at'] = datetime.datetime.now()
            token_response['expires_at'] = datetime.datetime.now() + datetime.timedelta(0, token_response['expires_in'])

            self.token = token_response
            self.auth_responses += self.token
        else:
            self.token = None
            self.auth_responses += response

        return response.request, response

    def refresh_token(self):
        """
        Update token, if expired.

        If the token is expired or does not exist yet, this method will create a new access token.

        :return: request, response for this request, or none, none if no new token is required
        """
        if not self.token or self.is_token_expired():
            return self.create_access_token()
        else:
            return None, None

    def get_access_token(self):
        """
        Returns a potentially set token.

        If the tokoen is already created or refreshed, it will get returned. Otherwise a None will get returned.

        :return: a created access_token or None
        """
        if "access_token" in self.token:
            return self.token["access_token"]
        else:
            return None

    def get_auth_headers(self, more: dict | None = None):
        """
        Create authentication headers and merge them with the 'more' headers.

        Use this method to create the authentication token header. If you got more headers to be added to this request
        please specify them as a dictionary using the 'more' - field.

        :param more: A dict containing more headers
        :return: a dict including auth headers and more headers to be added
        """
        merged = {
            'Authorization': f'Bearer {self.get_access_token()}',
        }

        if more:
            merged.update(more)

        return merged

    def is_token_expired(self):
        """
        Does an access token exist and is it not expired?

        :return: whether the access token is invalid or expired
        """
        if self.token and 'expires_at' in self.token:
            seconds_left = self.token_seconds_remaining()
            return seconds_left < 0
        else:
            return True

    def token_seconds_remaining(self):
        """
        How many seconds is the access token still valid?

        :return: seconds of validity, or 0 if no access token is created.
        """
        if self.token and 'expires_at' in self.token:
            return (self.token['expires_at'] - datetime.datetime.now()).total_seconds()
        else:
            return 0
