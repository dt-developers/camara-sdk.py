"""
CAMARA API Client

This small SDK abstracts from the defined [CAMARA](https://github.com/camaraproject)-apis.

Currently only the authentication and [Quality on Demand](https://github.com/camaraproject/QualityOnDemand) apis are
supported,
"""

from camara.Config import Config
from camara.Connectivity import Connectivity
from camara.Location import Location
from camara.QualityOnDemand import QualityOnDemand
from camara.TokenProvider import TokenProvider


class Camara:
    """
    Foundational class for all interactions with the CAMARA apis.

    It takes care of the authentication and renewal of tokens and provides an api for the specific sub Camara
    specification apis.

    Currently only "QoD" is supported by using the `qod` field.
    """

    def __init__(self, config):
        """
        Create a new CAMARA client.

        :param config: configuration for all endpoints.
        """

        self.config: Config = config
        self.token: dict | None = None
        self.authentication_responses: list = []
        if config.qod:
            self.qod: QualityOnDemand = QualityOnDemand(
                TokenProvider(config.qod.client_id, config.qod.client_secret, config.auth_url, config.verbose),
                config.qod
            )
        else:
            self.qod = None

        if config.connectivity:
            self.connectivity: Connectivity = Connectivity(
                TokenProvider(config.connectivity.client_id, config.connectivity.client_secret,
                              config.auth_url, config.verbose),
                config.connectivity
            )
        else:
            self.connectivity = None

        if config.location:
            self.location: Location = Location(
                TokenProvider(config.location.client_id, config.location.client_secret, config.auth_url,
                              config.verbose),
                config.location
            )
        else:
            self.location = None
