#!/usr/bin/env python3
"""
This is the entry point for the CAMARA APIs.

It provides a cli when called as a script, and calls apis specified in [CAMARA](https://github.com/camraproject).
"""
import sys
import json
import traceback
import camara
import camara.Config
from camara import Camara, QualityOnDemand
from camara.Utils import hsv, rgb_to_termcolor

# File to load at start for configuration of the cli
CONFIGURATION_FILE = ".camara.config"

# Set to 'None' to disable color. Otherwise, use an ANSI escape color code
# number from here: https://en.wikipedia.org/wiki/ANSI_escape_code
COLOR_INFO = 32
COLOR_ERROR = 41
COLOR_WARN = 43
COLOR_RAINBOW = 38
COLOR_EMPHASIZE = 1
COLOR_RAINBOW_INVERTED = "38;5;0;48"


def colorize(text, color=COLOR_INFO):
    """
    Take the text and colorize it with one color.

    This function can be used to colorize a piece of text for console output.

    :param text: which text to colorize
    :param color: which color to be taken.
    :return: a colorized version of the input text.
    """
    if color == COLOR_RAINBOW or color == COLOR_RAINBOW_INVERTED:
        result = ""
        for (index, char) in enumerate(text):
            code = rgb_to_termcolor(hsv(index * 360.0 / len(text), 1.0, 1.0))
            result += f"\033[{color};5;{code}m{char}"
        result += f"\033[m"
        return result
    elif color:
        return f"\033[{color}m{text}\033[m"
    else:
        return text


def variables(obj):
    return list(filter(lambda x: not x.startswith("__") and not callable(x), dir(obj)))


class Menu:
    """
    Creates a menu for the Command Line Interface.

    :param config: camara configuration loaded from specified file
    :return: nothing - on return the script ends
    """

    # Prompt for the user: Whenever this CLI asks the user something, this prompt appears
    PROMPT = colorize('CAMARA> ', COLOR_RAINBOW)

    def __init__(self, config):
        self.config = config
        self.config.to_ip = "0.0.0.0/8"
        self.config.from_ipv4 = None
        self.config.from_ipv6 = None
        self.config.from_number = None
        self.config.profile = QualityOnDemand.Profile.E
        self.config.duration = 10
        self.config.latitude = 52.49628951726823
        self.config.longitude = 13.358005137756487
        self.config.accuracy = 10

        self.verbs = {
            'help': self.user_help,
            'exit': self.user_exit,
            'set ipv4': self.user_set_from_ipv4,
            'set ipv6': self.user_set_from_ipv6,
            'set number': self.user_set_from_number,
            'time': self.user_time,
            'info': self.user_info,
            'api con': self.user_connectivity,
            'api loc': self.user_location,
            'set lat': self.user_location_set_latitude,
            'set lon': self.user_location_set_longitude,
            'set acc': self.user_location_set_accuracy,
            'api qod delete': self.user_delete_session,
            'api qod': self.create_session,
            'set prio': self.user_set_profile,
            'set to': self.user_qod_set_to,
            'set duration': self.user_qod_set_duration,
        }

        self.client = Camara(config)

    def start(self):
        """
        Start the menu, interacting with the user.
        """
        print()
        print(colorize("Welcome to the CAMARA management command line interface.", COLOR_RAINBOW))
        print()

        def call_verb(sel: str, param=None):
            if param is None:
                return self.verbs[sel]()
            else:
                return self.verbs[sel](param)

        go_on = True
        while go_on:
            selection = input(Menu.PROMPT)
            try:
                if selection in self.verbs:
                    go_on = call_verb(selection)
                else:
                    *s, parameter = selection.split(" ")
                    s = " ".join(s)
                    go_on = call_verb(s, parameter)

            except Exception as exception:
                # be graceful with exceptions: Print them and don't explode the cli.
                print(f"Error with verb '{selection}'. Try 'help' to list all the supported _verbs_.")
                print(f"{colorize('Exception caught', COLOR_RAINBOW_INVERTED)}:")
                traceback.print_exception(exception)

    def user_help(self):
        """Print help for all verbs."""

        print("Available verbs:")
        for key in sorted(self.verbs.keys()):
            documentation = self.verbs[key].__doc__
            if documentation:
                print(f"{colorize(f'▶ {key}', COLOR_EMPHASIZE)}: {documentation}")
            else:
                print(colorize(f'▶ {key}'))

        return True

    def user_info(self):
        """Print information about configuration."""

        for key in variables(self.config):
            value = getattr(self.config, key)

            if type(value) is camara.EndpointConfig.EndpointConfig:
                print(f"{key}: {[f'{x}: {getattr(value, x)}' for x in variables(value)]}")
            else:
                print(f"{key}: {value}")

        self.user_time()

        return True

    @staticmethod
    def request_input(old, new):
        if new is None:
            result = input(f"(old:{old})> ")
        else:
            result = new

        result_string = str(result)
        if len(result_string) <= 0 \
                or result_string.lower() == "none" \
                or result_string == "\'\'" \
                or result_string == "\"\"":
            result = None

        return result

    def user_qod_set_to(self, value=None):
        """Set to ip address. The ip of the device the connection should start from."""
        self.config.to_ip = self.request_input(self.config.to_ip, value)
        return True

    def user_set_from_ipv4(self, value=None):
        """Set ipv4 address it should originate from. The ip the device connects to."""
        self.config.from_ipv4 = self.request_input(self.config.from_ipv4, value)
        return True

    def user_set_from_ipv6(self, value=None):
        """Set ipv6 address the phone is using. The ip the device connects to."""
        self.config.from_ipv6 = self.request_input(self.config.from_ipv6, value)
        return True

    def user_set_profile(self, value=None):
        """Set qod prioritization profile S,M,L,E."""
        self.config.profile = self.request_input(self.config.profile, value)
        if self.config.profile.lower() in ["s", "m", "l", "e"]:
            if self.config.profile.lower() == "s":
                self.config.profile = QualityOnDemand.Profile.S

            elif self.config.profile.lower() == "m":
                self.config.profile = QualityOnDemand.Profile.M

            elif self.config.profile.lower() == "l":
                self.config.profile = QualityOnDemand.Profile.L

            elif self.config.profile.lower() == "e":
                self.config.profile = QualityOnDemand.Profile.E
        else:
            print(colorize("Warning: No s,m,l, or e given. Defaulting to 'E'.", COLOR_WARN))
            self.config.profile = QualityOnDemand.Profile.E

        return True

    def user_set_from_number(self, value=None):
        """Set phone number to be used. The ip the device connects to."""
        self.config.from_number = self.request_input(self.config.from_number, value)
        return True

    def user_qod_set_duration(self, value=None):
        """Set duration of newly created sessions in seconds."""
        self.config.duration = self.request_input(self.config.duration, value)
        return True

    def create_session(self):
        """Create a qos session using one of the defined qos classes. Needs 'from_XXX', 'to', and 'duration' values."""
        request, response = self.client.qod.create_session(
            qos=self.config.profile,
            from_ipv4=self.config.from_ipv4,
            from_ipv6=self.config.from_ipv6,
            from_number=self.config.from_number,
            to_ip=self.config.to_ip,
            duration=self.config.duration
        )

        self.print_request_response(request, response)
        return True

    def user_delete_session(self):
        """Delete last session."""
        if self.client.qod.last_session and 'id' in self.client.qod.last_session:
            session_id = self.client.qod.last_session['id']
            request, response = self.client.qod.delete_session(session_id)
            self.print_request_response(request, response)
        else:
            print("No session.")
        return True

    def user_connectivity(self):
        """Request connectivity information from the `from_ip`."""
        request, response = self.client.connectivity.get_status(self.config.from_ipv6, self.config.from_number)
        self.print_request_response(request, response)
        return True

    def user_location(self):
        """Request location information from the `from_ip`."""
        request, response = self.client.location.get_location(
            self.config.from_ipv4,
            self.config.from_ipv6,
            self.config.from_number,
            self.config.latitude,
            self.config.longitude,
            self.config.accuracy,
        )
        self.print_request_response(request, response)
        return True

    def user_location_set_latitude(self, value=None):
        """Set the latitude for the center."""
        self.config.latitude = self.request_input(self.config.latitude, value)
        return True

    def user_location_set_longitude(self, value=None):
        """Set the longitude for the center."""
        self.config.longitude = self.request_input(self.config.longitude, value)
        return True

    def user_location_set_accuracy(self, value=None):
        """Set the accuracy for the location to be considered inside."""
        self.config.accuracy = self.request_input(self.config.accuracy, value)
        return True

    def user_time(self):
        """Print seconds left on session and token."""
        if self.client.qod.last_session:
            left = self.client.qod.session_seconds_remaining()
            print(f"{int(left)}s left in session duration.")
        else:
            print("No session.")

        print()

        for entry in [
            ("qod", self.client.qod.token_provider),
            ("con", self.client.connectivity.token_provider),
            ("loc", self.client.location.token_provider)
        ]:
            name, provider = entry
            if provider.is_token_expired():
                print(f"{name} token expired.")
            else:
                print(f"{name} token has {int(provider.token_seconds_remaining())}s in duration left.")

        return True

    @staticmethod
    def user_exit():
        """Close this menu."""
        return False

    @staticmethod
    def print_request_response(request, response):
        """Helper function for printing the request and response, humanfriendly."""
        print(f"request: {request.body}")
        if 'status' in response:
            status = response['status']
        else:
            status = 'no-status'
        print(f"response: {status} {response}")


# Are we in interactive / scripting mode?
if __name__ == "__main__":
    if '--help' in sys.argv or '-h' in sys.argv:
        print(colorize("Camara CLI", COLOR_RAINBOW))
        print("\n\nNo parameters needed, use the config file. Create one with '--generate-dummy-config' or '-g'.")
    elif '--generate-dummy-config' in sys.argv or '-g' in sys.argv:
        c = camara.Config(
            auth_url="localhost:8000",
            qod=camara.EndpointConfig.EndpointConfig(
                client_id="",
                client_secret="",
                base_url=""
            ),
            connectivity=camara.EndpointConfig.EndpointConfig(
                client_id="",
                client_secret="",
                base_url=""
            ),
            location=camara.EndpointConfig.EndpointConfig(
                client_id="",
                client_secret="",
                base_url=""
            ),
            version=0
        )

        open(CONFIGURATION_FILE, "w").write(json.dumps(c, default=vars, indent=2))
        print(colorize(f"Saved configuration in {CONFIGURATION_FILE}.", COLOR_WARN))
    else:
        try:
            conf = camara.Config.create_from_file(CONFIGURATION_FILE)
        except FileNotFoundError:
            print(
                colorize(
                    "Could not find configuration '.camara.conf'.\n\n"
                    "Please create one with '--generate-dummy-config'.",
                    COLOR_ERROR
                )
            )

        except json.decoder.JSONDecodeError as error:
            print(colorize("Invalid configuration given.", COLOR_ERROR))
            print(error)

        except TypeError as error:
            print(colorize("Invalid configuration file.", COLOR_ERROR))
            print(error)

        else:
            Menu(conf).start()
