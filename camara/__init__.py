"""
CAMARA API Client

This small SDK abstracts from the defined [CAMARA](https://github.com/camaraproject)-apis.

Currently only the authentication and [Quality on Demand](https://github.com/camaraproject/QualityOnDemand) apis are
supported,
"""

import datetime
import json

import requests
from enum import Enum

# base url for authentication
OPENID_CONNECT_URL = "https://playground.spacegate.telekom.de/auth/realms/default/protocol/openid-connect/token"


class Camara:
    """
    Foundational class for all interactions with the CAMARA apis.

    It takes care of the authentication and renewal of tokens and provides an api for the specific sub Camara
    specification apis.

    Currently only "QoD" is supported by using the `qod` field.
    """

    def __init__(
            self,
            client_id: str,
            client_secret: str,
            authentication_url: str = OPENID_CONNECT_URL
    ):
        """
        Create a new CAMARA client.

        :param client_id: the client id specified by your CAMARA representative.
        :param client_secret: the secret you got together with the client id.
        :param authentication_url: Address of the authentication server. Defaults to DT authentication.
        """

        self.authentication_url: str = authentication_url
        self.token: dict | None = None
        self.authentication_responses: list = []
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.qod: QualityOnDemand = QualityOnDemand(self)

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

        response = requests.request("POST", self.authentication_url, headers=headers, data=payload)

        if response.status_code == 200:
            self.token = response.json()
            self.token['created_at'] = datetime.datetime.now()
            self.token['expires_at'] = datetime.datetime.now() + datetime.timedelta(0, self.token['expires_in'])
            self.authentication_responses += self.token
        else:
            self.token = None
            self.authentication_responses += response

        return response.request, response.json()

    def refresh_token(self):
        """
        Update token, if expired.

        If the token is expired or does not exist yet, this method will create a new access token.

        :return: request, response for this request, or none, none if no new token is required
        """
        if not self.token or self.is_token_expired():
            request, response = self.create_access_token()
            self.token = response
            return request, response
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
        Create authentication headers and merge them with the 'more' headrs.

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


class QualityOnDemand:
    """
    Specific CAMARA API: Quality on Demand

    This set of rest operations control the quality on demand aspects of a network channel. It prioritizes network
    traffic based on a specific qod profile.
    """

    class Profile(Enum):
        """
        Enumeration holding all valid values for QoD profiles.
        """
        E = "QOD_E"
        S = "QOD_S"
        M = "QOD_M"
        L = "QOD_L"

    def __init__(self, token_provider):
        self.token_provider = token_provider
        self.last_session: dict | None = None
        self.responses: list = []
        self.base_url: str = "https://playground.spacegate.telekom.de/hnce/qod/v0/sessions"

    def create_session(
            self,
            qos: Profile,
            from_ip: str,
            to_ip: str = "0.0.0.0/0",
            duration: int = 10,
    ):
        """
        Create a new qod session, prioritizing traffic.

        :param qos: QOD_E, QOD_S, QOD_M, QOD_L?
        :param from_ip:
        :param to_ip:
        :param duration:
        :return: request, response tuple for the actual rest call
        """
        self.token_provider.refresh_token()

        payload = json.dumps({
            "duration": duration,
            "ueId": {
                "ipv4addr": from_ip
            },
            "asId": {
                "ipv4addr": to_ip
            },
            "qos": qos.value
        })

        headers = self.token_provider.get_auth_headers({'Content-Type': 'application/json'})
        response = requests.request(
            "POST",
            self.base_url,
            headers=headers,
            data=payload
        )

        if response.ok:
            self.last_session = response.json()
            self.last_session['expires_at'] = datetime.datetime.now() + datetime.timedelta(0, duration)

        return response.request, response.json()

    def delete_session(self, session_id: str):
        """
        Deletes the session as identified by its session id.

        :param session_id: the id of the session to be deleted
        :return: request, response of the operation call
        """
        self.token_provider.refresh_token()

        url = f"{self.base_url}/{session_id}"
        response = requests.request("DELETE", url, headers=self.token_provider.get_auth_headers())
        return response.request, response

    def get_session(self, session_id: str):
        """
        Returns the session identified by the given id.

        :param session_id: Which session to return?
        :return: the request and response(session) of this call.
        """
        self.token_provider.refresh_token()

        url = f"{self.base_url}/{session_id}"
        response = requests.request("GET", url, headers=self.token_provider.get_auth_headers())

        request = response.request
        response = response.json()
        return request, response

    def is_session_expired(self):
        """
        Is the last created session still active?

        :return: False if the session exists and is still active, otherwise True.
        """
        if self.last_session and 'expires_at' in self.last_session:
            seconds_left = self.session_seconds_remaining()
            return seconds_left < 0
        else:
            return True

    def session_seconds_remaining(self):
        """
        How long is the last created session still active? (in seconds)
        :return: seconds remaining on the active session, or 0 if no session exists.
        """
        if self.last_session and 'expires_at' in self.last_session:
            return (self.last_session['expires_at'] - datetime.datetime.now()).total_seconds()
        else:
            return 0
