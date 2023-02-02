import datetime
import json

import requests

OPENID_CONNECT_URL = "https://playground.spacegate.telekom.de/auth/realms/default/protocol/openid-connect/token"


class Camara:
    def __init__(self,
                 client_id,
                 client_secret,
                 authentication_url=OPENID_CONNECT_URL):
        self.authentication_url = authentication_url
        self.token = None
        self.authentication_responses = []
        self.client_id = client_id
        self.client_secret = client_secret
        self.qod = QualityOnDemand(self)

    def create_access_token(self):
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
        if not self.token or self.is_token_expired():
            _, response = self.create_access_token()
            self.token = response

    def get_access_token(self):
        if "access_token" in self.token:
            return self.token["access_token"]
        else:
            return "no token"

    def get_auth_headers(self, more=None):
        merged = {
            'Authorization': f'Bearer {self.get_access_token()}',
        }

        if more:
            merged.update(more)

        return merged

    def is_token_expired(self):
        if self.token and 'expires_at' in self.token:
            seconds_left = self.token_seconds_remaining()
            return seconds_left < 0
        else:
            return True

    def token_seconds_remaining(self):
        if self.token and 'expires_at' in self.token:
            return (self.token['expires_at'] - datetime.datetime.now()).total_seconds()
        else:
            return 0


class QualityOnDemand:
    def __init__(self, token_provider):
        self.token_provider = token_provider
        self.last_session = None
        self.responses = []
        self.base_url = "https://playground.spacegate.telekom.de/hnce/qod/v0/sessions"

    def create_session(
            self,
            qos,
            from_ip,
            to_ip="0.0.0.0/0",
            duration=10,
    ):
        self.token_provider.refresh_token()

        payload = json.dumps({
            "duration": duration,
            "ueId": {
                "ipv4addr": from_ip
            },
            "asId": {
                "ipv4addr": to_ip
            },
            "qos": qos
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

    def delete_session(self, session_id):
        self.token_provider.refresh_token()

        url = f"{self.base_url}/{session_id}"
        response = requests.request("DELETE", url, headers=self.token_provider.get_auth_headers())
        return response.request, response

    def get_session(self, session_id):
        self.token_provider.refresh_token()

        url = f"{self.base_url}/{session_id}"
        response = requests.request("GET", url, headers=self.token_provider.get_auth_headers())

        request = response.request
        response = response.json()
        return request, response

    def is_session_expired(self):
        if self.last_session and 'expires_at' in self.last_session:
            seconds_left = self.session_seconds_remaining()
            return seconds_left < 0
        else:
            return True

    def session_seconds_remaining(self):
        if self.last_session and 'expires_at' in self.last_session:
            return (self.last_session['expires_at'] - datetime.datetime.now()).total_seconds()
        else:
            return 0
