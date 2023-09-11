from camara.EndpointConfig import EndpointConfig
from camara.QualityOnDemand import Profile
from camara.QualityOnDemand import normalize_profile
from camara.Utils import colorize
from camara.Utils import TermColor
import json


class Config:
    """
    Configuration Abstraction

    Used internally to store the configuration values for the sdk.
    """

    def __init__(
            self,
            auth_url: str,
            qod: EndpointConfig,
            connectivity: EndpointConfig,
            location: EndpointConfig,
            version: int = 1,
            verbose: bool = False,
            to_ip=None,
            from_ipv4=None,
            from_ipv6=None,
            from_number=None,
            profile=None,
            duration=None,
            latitude=None,
            longitude=None,
            accuracy=None,
    ):
        self.version: int = version
        self.auth_url: str = auth_url
        self.qod: EndpointConfig = qod
        self.connectivity: EndpointConfig = connectivity
        self.location: EndpointConfig = location
        self.verbose: bool = verbose
        self.to_ip: str = to_ip
        self.from_ipv4: str = from_ipv4
        self.from_ipv6: str = from_ipv6
        self.from_number: str = from_number
        self.profile: Profile = profile
        self.duration: int = duration
        self.latitude: float = latitude
        self.longitude: float = longitude
        self.accuracy: int = accuracy


def create_from_file(filename):
    config_json = json.loads(open(filename).read())
    if 'qod' in config_json:
        config_json['qod'] = EndpointConfig(**config_json['qod'])

    if 'connectivity' in config_json:
        config_json['connectivity'] = EndpointConfig(**config_json['connectivity'])

    if 'location' in config_json:
        config_json['location'] = EndpointConfig(**config_json['location'])

    if 'profile' in config_json:
        config_json['profile'] = normalize_profile(config_json['profile'])

        if config_json['profile'] is None:
            print(
                colorize(
                    f"Reading configuration file, but profile '{config_json['profile']}' not found, please use 'S','M','L',"
                    f" or 'E'. Defaulting back to 'E'.",
                    TermColor.COLOR_ERROR
                )
            )
            config_json['profile'] = Profile.E
    return Config(**config_json)
