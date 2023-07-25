import datetime
import json
from enum import Enum

import requests

from camara.EndpointConfig import EndpointConfig
from camara.Utils import set_ue_id, remove_empty


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
        E = "QOS_E"
        S = "QOS_S"
        M = "QOS_M"
        L = "QOS_L"

    def __init__(self, token_provider, config: EndpointConfig):
        self.token_provider = token_provider
        self.last_session: dict | None = None
        self.responses: list = []
        self.config = config
        self.base_url: str = config.base_url

    def create_session(
            self,
            qos: Profile,
            from_ipv4: str | None,
            from_ipv6: str | None,
            from_number: str | None,
            to_ip: str,
            duration: int,
    ):
        """
        Create a new qod session, prioritizing traffic.

        :param qos: QOD_E, QOD_S, QOD_M, QOD_L?
        :param from_ipv4:
        :param from_ipv6:
        :param from_number:
        :param to_ip:
        :param duration:
        :return: request, response tuple for the actual rest call
        """
        self.token_provider.refresh_token()

        payload = {
            "duration": duration,
            "ueId": {
            },
            "asId": {
                "ipv4addr": to_ip
            },
            "qos": qos.value
        }

        set_ue_id(payload, from_ipv4, from_ipv6, from_number)

        headers = self.token_provider.get_auth_headers({'Content-Type': 'application/json'})
        response = requests.request(
            "POST",
            self.base_url,
            headers=headers,
            data=json.dumps(remove_empty(payload))
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
