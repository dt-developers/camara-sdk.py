import json

import requests

from camara.EndpointConfig import EndpointConfig
from camara.Utils import set_ue_id
from camara.Utils import remove_empty


class Location:
    """
    Api for device location vicinity
    """

    def __init__(self, token_provider, config: EndpointConfig):
        self.token_provider = token_provider
        self.responses: list = []
        self.config = config
        self.base_url: str = config.base_url

    def get_location(self, from_ipv4: str, from_ipv6: str, from_number: str, latitude: float, longitude: float,
                     accuracy: float):
        """
        :param from_ipv4: the ip of the device, you want to know if it's in the vicinity
        :param from_ipv6: the ip of the device, you want to know if it's in the vicinity
        :param from_number: the phone number of the handset (ue)
        :param latitude: the latitudinal coordinate on earth, centering the circle
        :param longitude: the longitudinal coordinate on earth, centering the circle
        :param accuracy: the distance from the location specified, still considered as containing the device.
        :return: request, response tuple for the actual rest call, identifying where the phone is.
        """
        self.token_provider.refresh_token()

        payload = {
            "ueId": {
            },
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": accuracy,
        }

        set_ue_id(payload, from_ipv4, from_ipv6, from_number)

        headers = self.token_provider.get_auth_headers({'Content-Type': 'application/json'})
        response = requests.request(
            "POST",
            self.base_url,
            headers=headers,
            data=json.dumps(remove_empty(payload))
        )

        return response.request, response.json()
