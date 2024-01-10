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
from camara.Config import create_from_file
from camara import Camara
from camara.QualityOnDemand import Profile
from camara.QualityOnDemand import normalize_profile
from camara.Utils import latitude_for_km, longitude_for_km, print_request_response, colorize, variables
from camara.Utils import TermColor

# File to load at start for configuration of the cli
CONFIGURATION_FILE = ".camara.config"


class Menu:
    """
    Creates a menu for the Command Line Interface.

    :param config: camara configuration loaded from specified file
    :return: nothing - on return the script ends
    """

    # Prompt for the user: Whenever this CLI asks the user something, this prompt appears
    PROMPT = colorize('CAMARA> ', TermColor.COLOR_RAINBOW)

    def __init__(self, config):
        self.config = config

        self.verbs = {
            'help': self.user_help,
            'exit': self.user_exit,
            'set ipv4': self.user_set_from_ipv4,
            'set ipv6': self.user_set_from_ipv6,
            'set number': self.user_set_from_number,
            'set verbose': self.user_set_verbose,
            'time': self.user_time,
            'tokens': self.user_tokens,
            'info': self.user_info,
            'api con': self.user_connectivity,
            'api loc': self.user_location,
            'xxx': self.user_experiment,
            'set lat': self.user_location_set_latitude,
            'set lon': self.user_location_set_longitude,
            'set acc': self.user_location_set_accuracy,
            'api qod delete': self.user_delete_session,
            'api qod get': self.user_get_session,
            'api qod': self.user_create_session,
            'set profile': self.user_set_profile,
            'set to': self.user_qod_set_to,
            'set duration': self.user_qod_set_duration,
        }

        self.client = Camara(config)

    def start(self):
        """
        Start the menu, interacting with the user.
        """
        print()
        print(colorize("Welcome to the CAMARA management command line interface.", TermColor.COLOR_RAINBOW))
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
                print(f"{colorize('Exception caught', TermColor.COLOR_RAINBOW_INVERTED)}: "
                      f"{type(exception)} ({exception})")

                if self.config.verbose:
                    traceback.print_exception(exception)

    def user_help(self):
        """Print help for all verbs."""

        print("Available verbs:")
        for key in sorted(self.verbs.keys()):
            documentation = self.verbs[key].__doc__
            if documentation:
                print(f"{colorize(f'▶ {key}', TermColor.COLOR_EMPHASIZE)}: {documentation}")
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
        self.config.profile = normalize_profile(self.request_input(self.config.profile, value))

        if self.config.profile is None:
            print(colorize("Warning: No 's','m','l', or 'e' profile given. Defaulting to 'e'.", TermColor.COLOR_WARN))
            self.config.profile = Profile.E

        return True

    def user_set_from_number(self, value=None):
        """Set phone number to be used. The ip the device connects to."""
        self.config.from_number = self.request_input(self.config.from_number, value).replace(" ","")
        return True

    def user_set_verbose(self, value=None):
        """Set or unset verbose output (True, False)."""
        self.config.verbose = self.request_input(self.config.verbose, value)
        self.config.verbose = self.config.verbose.lower() == "true"
        return True

    def user_qod_set_duration(self, value=None):
        """Set duration of newly created sessions in seconds."""
        self.config.duration = int(self.request_input(self.config.duration, value))
        return True

    def user_create_session(self):
        """Create a qos session using one of the defined qos classes. Needs 'from_XXX', 'to', and 'duration' values."""
        if not self.client.qod:
            print(colorize("Api not configured.", TermColor.COLOR_WARN))
            return True

        request, response = self.client.qod.create_session(
            qos=self.config.profile,
            from_ipv4=self.config.from_ipv4,
            from_ipv6=self.config.from_ipv6,
            from_number=self.config.from_number,
            to_ip=self.config.to_ip,
            duration=self.config.duration
        )

        print_request_response(request, response, self.config.verbose)
        return True

    def user_get_session(self):
        """Get the session created."""

        if not self.client.qod:
            print(colorize("Api not configured.", TermColor.COLOR_WARN))
            return True

        if self.client.qod.last_session and 'id' in self.client.qod.last_session:
            session = self.client.qod.last_session['id']
        else:
            session = ''

        request, response = self.client.qod.get_session(
            session_id=session
        )

        print_request_response(request, response, self.config.verbose)
        return True

    def user_delete_session(self):
        """Delete last session."""
        if not self.client.qod:
            print(colorize("Api not configured.", TermColor.COLOR_WARN))
            return True

        if self.client.qod.last_session and 'id' in self.client.qod.last_session:
            session_id = self.client.qod.last_session['id']
            request, response = self.client.qod.delete_session(session_id)
            print_request_response(request, response, self.config.verbose)
        else:
            print("No session.")
        return True

    def user_connectivity(self):
        """Request connectivity information from the `from_ip`."""
        if not self.client.connectivity:
            print(colorize("Api not configured.", TermColor.COLOR_WARN))
            return True

        request, response = self.client.connectivity.get_status(self.config.from_ipv6, self.config.from_number)
        print_request_response(request, response, self.config.verbose)
        return True

    def user_location(self):
        """Request location information from the `from_ip`."""
        if not self.client.location:
            print(colorize("Api not configured.", TermColor.COLOR_WARN))
            return True

        request, response = self.client.location.get_location(
            self.config.from_ipv4,
            self.config.from_ipv6,
            self.config.from_number,
            self.config.latitude,
            self.config.longitude,
            self.config.accuracy,
        )
        print_request_response(request, response, self.config.verbose)

        return True

    def user_experiment(self):
        """."""
        request, response = self.client.location.get_location(
            self.config.from_ipv4,
            self.config.from_ipv6,
            self.config.from_number,
            self.config.latitude,
            self.config.longitude,
            self.config.accuracy,
        )
        print_request_response(request, response, self.config.verbose)

        accuracy = float(self.config.accuracy)
        latitude = float(self.config.latitude)
        longitude = float(self.config.longitude)
        while response.json()["verificationResult"] == 'true':
            print(
                colorize(
                    f"Found you within {accuracy}km accuracy. Digging deeper.",
                    TermColor.COLOR_RAINBOW_INVERTED
                )
            )

            accuracy *= 0.75
            for (x, y) in (
                    (-1, -1), (-1, 0), (-1, 1),
                    (0, -1), (0, 0), (0, 1),
                    (1, -1), (1, 0), (1, 1),
                    (-0.5, -0.5), (-0.5, 0.5),
                    (0.5, -0.5), (0.5, 0.5),
            ):
                request, response = self.client.location.get_location(
                    self.config.from_ipv4,
                    self.config.from_ipv6,
                    self.config.from_number,
                    latitude + x * latitude_for_km(latitude, longitude, accuracy),
                    longitude + y * longitude_for_km(longitude, longitude, accuracy),
                    accuracy,
                )

                if self.config.verbose:
                    print_request_response(request, response, self.config.verbose)

                if not response.ok or response.json()["verificationResult"] == 'true':
                    break

            if response.json()["verificationResult"] == 'true':
                latitude = latitude + x * latitude_for_km(latitude, longitude, accuracy)
                longitude = longitude + y * longitude_for_km(latitude, longitude, accuracy)

                print(f"You are somewhere here: {latitude} x {longitude} @ {accuracy}km")

        else:
            print(
                colorize(
                    f"Couldn't find you, increase {accuracy}km accuracy or initial position.",
                    TermColor.COLOR_RAINBOW_INVERTED
                )
            )

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
            if left >= 0:
                print(f"{int(left)}s left in session duration.")
            else:
                print(f"The session is done.")
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

    def user_tokens(self):
        """Print tokens."""

        for entry in [
            ("qod", self.client.qod.token_provider),
            ("con", self.client.connectivity.token_provider),
            ("loc", self.client.location.token_provider)
        ]:
            name, provider = entry
            if provider.is_token_expired():
                print(f"{name} token expired.\n"
                      f"It was '{provider.token}'.")
            else:
                print(
                    f"{name} token has {int(provider.token_seconds_remaining())}s in duration left.\n"
                    f"Use it as '{provider.token}'."
                )

        return True

    @staticmethod
    def user_exit():
        """Close this menu."""
        return False


# Are we in interactive / scripting mode?
if __name__ == "__main__":
    if '--help' in sys.argv or '-h' in sys.argv:
        print(colorize("Camara CLI", TermColor.COLOR_RAINBOW))
        print("\n\nNo parameters needed, use the config file. Create one with '--generate-dummy-config' or '-g'.")
    elif '--generate-dummy-config' in sys.argv or '-g' in sys.argv:
        c = camara.Config(
            auth_url="localhost:8000",
            version=0
        )

        open(CONFIGURATION_FILE, "w").write(json.dumps(c, default=vars, indent=2))
        print(colorize(f"Saved configuration in {CONFIGURATION_FILE}.", TermColor.COLOR_WARN))
    else:
        try:
            conf = create_from_file(CONFIGURATION_FILE)
        except FileNotFoundError:
            print(
                colorize(
                    "Could not find configuration '.camara.conf'.\n\n"
                    "Please create one with '--generate-dummy-config'.",
                    TermColor.COLOR_ERROR
                )
            )

        except json.decoder.JSONDecodeError as error:
            print(colorize("Invalid configuration given.", TermColor.COLOR_ERROR))
            print(error)

        except TypeError as error:
            print(colorize("Invalid configuration file.", TermColor.COLOR_ERROR))
            print(error)

        else:
            Menu(conf).start()
