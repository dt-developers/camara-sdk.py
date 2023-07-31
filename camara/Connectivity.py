import json

import requests

from camara.EndpointConfig import EndpointConfig
from camara.Utils import set_ue_id
from camara.Utils import remove_empty


class Connectivity:
    """
    Specific CAMARA API: Phone Status
    """

    def __init__(self, token_provider, config: EndpointConfig):
        self.token_provider = token_provider
        self.responses: list = []
        self.config = config
        self.base_url: str = config.base_url

    def get_status(self, ipv6: str, phone_number: str):
        """
        :param ipv6:
        :param phone_number:
        :return: request, response tuple for the actual rest call
        """
        self.token_provider.refresh_token()

        payload = {
            "ueId": {
            },
            "eventType": "UE_ROAMING_STATUS"
        }

        set_ue_id(payload, None, ipv6, phone_number)

        headers = self.token_provider.get_auth_headers({'Content-Type': 'application/json'})
        response = requests.request(
            "POST",
            self.base_url,
            headers=headers,
            data=json.dumps(remove_empty(payload))
        )

        return response.request, response
