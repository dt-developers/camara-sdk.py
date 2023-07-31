from camara.EndpointConfig import EndpointConfig
import json


class Config:
    """
    Configuration Abstraction

    Used internally to store the configuration values for the sdk.
    """

    @classmethod
    def create_from_file(cls, filename):
        config_json = json.loads(open(filename).read())
        config_json['qod'] = EndpointConfig(**config_json['qod'])
        config_json['connectivity'] = EndpointConfig(**config_json['connectivity'])
        config_json['location'] = EndpointConfig(**config_json['location'])
        return Config(**config_json)

    def __init__(
            self,
            auth_url: str,
            qod: EndpointConfig,
            connectivity: EndpointConfig,
            location: EndpointConfig,
            version: int = 1,
            verbose: bool = False,
    ):
        self.version: int = version
        self.auth_url: str = auth_url
        self.qod: EndpointConfig = qod
        self.connectivity: EndpointConfig = connectivity
        self.location: EndpointConfig = location
        self.verbose: bool = verbose
