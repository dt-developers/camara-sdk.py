import json

import requests

from camara.EndpointConfig import EndpointConfig


class Connectivity:
    """
    Specific CAMARA API: Phone Status
    """

    def __init__(self, token_provider, config: EndpointConfig):
        self.token_provider = token_provider
        self.responses: list = []
        self.config = config
        self.base_url: str = config.base_url

    def get_status(self, from_ip: str):
        """
        :param from_ip:
        :return: request, response tuple for the actual rest call
        """
        self.token_provider.refresh_token()

        payload = json.dumps({
            "ueId": {
                "ipv4addr": from_ip,
            },
            "eventType": ""
        })

        headers = self.token_provider.get_auth_headers({'Content-Type': 'application/json'})
        response = requests.request(
            "POST",
            self.base_url,
            headers=headers,
            data=payload
        )

        return response.request, response.json()
