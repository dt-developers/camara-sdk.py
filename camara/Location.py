import json

import requests

from camara.EndpointConfig import EndpointConfig


class Location:
    """
    Api for device location vicinity
    """

    def __init__(self, token_provider, config: EndpointConfig):
        self.token_provider = token_provider
        self.responses: list = []
        self.config = config
        self.base_url: str = config.base_url

    def get_location(self, from_ip: str, latitude: float, longitude: float, accuracy: float):
        """
        :param from_ip: the ip of the device, you want to know if it's in the vicinity
        :param latitude: the latitudinal coordinate on earth, centering the circle
        :param longitude: the longitudinal coordinate on earth, centering the circle
        :param accuracy: the distance from the location specified, still considered as containing the device.
        :return: request, response tuple for the actual rest call, identifying where the phone is.
        """
        self.token_provider.refresh_token()

        payload = json.dumps({
            "ueId": {
                "ipv4addr": from_ip
            },
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": accuracy,
        })

        headers = self.token_provider.get_auth_headers({'Content-Type': 'application/json'})
        response = requests.request(
            "POST",
            self.base_url,
            headers=headers,
            data=payload
        )

        return response.request, response.json()
